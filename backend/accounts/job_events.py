"""Service job events → field notifications, office notifications, live field refresh.

Job saves are diffed against the row as it was before the save (pre_save
snapshot), so every write path (office form, confirm, sale scheduling, field
submit, delete) produces the same events:

field (technicians the job is visible to)
    assigned      job became visible to the technician
    rescheduled   still theirs, date/time changed
    unassigned    taken away (reassigned / sent back to pending)
    cancelled     job deleted
office (service leads)
    job_new       organic service job created
    job_scheduled mount job got its day (pending → open)
    job_submitted field delivered the job
"""

from django.db.models.signals import post_delete, post_save, pre_delete, pre_save

from .models import Notification
from .notifications import notify, users_with
from .realtime import send_to_users

SNAP_FIELDS = ('status', 'assignee_id', 'assign_all', 'date', 'time')


def _url(getter) -> str:
    from django.urls import NoReverseMatch

    try:
        return getter()
    except NoReverseMatch:
        return ''


def _snapshot(job) -> dict:
    return {name: getattr(job, name) for name in SNAP_FIELDS}


def _field_user_ids(snap: dict) -> set:
    """Users of crew members that see this job in the field app."""
    from crew.models import CrewMember
    from service.models import Job

    if not snap or snap['status'] != Job.STATUS_OPEN:
        return set()
    ids = set()
    if snap['assign_all']:
        ids.update(
            CrewMember.objects.filter(is_active=True, user__isnull=False, user__is_active=True)
            .values_list('user_id', flat=True)
        )
    if snap['assignee_id']:
        uid = CrewMember.objects.filter(pk=snap['assignee_id']).values_list('user_id', flat=True).first()
        if uid:
            ids.add(uid)
    return ids


def _when(day, at) -> str:
    from service.field_views import long_day, relative_day
    from django.utils import timezone

    if not day:
        return ''
    text = long_day(day)
    if at:
        text += f' {at.strftime("%H:%M")}'
    rel = relative_day(day, timezone.localdate())
    return f'{text} ({rel})' if rel not in ('Bugün', 'Yarın') else f'{rel} · {text}'


def _device(job) -> str:
    try:
        summary = job.device_summary
    except Exception:  # noqa: BLE001 — packs may not exist yet mid-create
        summary = '—'
    if summary and summary != '—':
        return summary
    sale = getattr(job, 'sale', None)
    if sale is not None:
        line = sale.lines.select_related('product').filter(product__is_device=True).first()
        if line and line.product_id:
            return line.product.display_name
    return ''


def _short_day(day, at) -> str:
    from service.field_views import TR_DOW_LONG

    if not day:
        return ''
    text = TR_DOW_LONG[day.weekday()]
    return f'{text} {at.strftime("%H:%M")}' if at else text


def _field_events(job, before: dict, after: dict, actor_id) -> None:
    from service.models import Job

    old_ids = _field_user_ids(before)
    new_ids = _field_user_ids(after)
    party = job.party.display_name
    kind = 'montaj' if job.is_mount else 'servis işi'
    url = _url(job.get_field_url)
    added = new_ids - old_ids
    removed = old_ids - new_ids
    kept = old_ids & new_ids
    if added:
        device = _device(job)
        when = _when(job.date, job.time)
        notify(
            added,
            kind=Notification.KIND_JOB_ASSIGNED,
            title=f'Yeni {kind} · {party}',
            body=' — '.join(p for p in (device, when) if p),
            url=url,
            actor=actor_id,
        )
    if removed and after.get('status') in (Job.STATUS_OPEN, Job.STATUS_PENDING):
        given = after.get('status') == Job.STATUS_OPEN and after.get('assignee_id')
        notify(
            removed,
            kind=Notification.KIND_JOB_UNASSIGNED,
            title=f'{"İş başkasına verildi" if given else "İş sizden alındı"} · {job.display_number}',
            body=party,
            url='',
            actor=actor_id,
        )
    if kept and (before['date'] != after['date'] or before['time'] != after['time']):
        notify(
            kept,
            kind=Notification.KIND_JOB_RESCHEDULED,
            title=f'{"Montaj" if job.is_mount else "Servis"} günü değişti · {party}',
            body=f'{_short_day(before["date"], before["time"])} → {_when(after["date"], after["time"])}',
            url=url,
            actor=actor_id,
        )
    touched = old_ids | new_ids
    if touched:
        send_to_users(touched, 'field', actor_id=actor_id, obj_id=job.pk)


def _office_events(job, before, after: dict, created: bool, actor_id) -> None:
    from service.models import Job

    leads = None

    def lead_ids():
        # Leads who also get the field "assigned" notice for this job skip the office copy.
        nonlocal leads
        if leads is None:
            in_field = _field_user_ids(after)
            leads = [user.pk for user in users_with('can_service_lead') if user.pk not in in_field]
        return leads

    party = job.party.display_name
    if created and not job.sale_id:
        notify(
            lead_ids(),
            kind=Notification.KIND_JOB_NEW,
            title=f'Yeni servis işi · {party}',
            body=' · '.join(p for p in (job.number, _when(job.date, job.time)) if p),
            url=_url(job.get_absolute_url),
            actor=actor_id,
            send_push=False,
        )
    if (
        job.sale_id
        and after['status'] == Job.STATUS_OPEN
        and (created or (before and before['status'] == Job.STATUS_PENDING))
    ):
        notify(
            lead_ids(),
            kind=Notification.KIND_JOB_SCHEDULED,
            title=f'Montaj günü kesinleşti · {party}',
            body=' · '.join(p for p in (job.display_number, _when(job.date, job.time)) if p),
            url=_url(job.get_absolute_url),
            actor=actor_id,
            send_push=False,
        )
    if after['status'] == Job.STATUS_SUBMITTED and before and before['status'] != Job.STATUS_SUBMITTED:
        notify(
            lead_ids(),
            kind=Notification.KIND_JOB_SUBMITTED,
            title=f'İş teslim edildi · {party}',
            body=' · '.join(p for p in (job.display_number, job.assignee_label) if p),
            url=_url(job.get_absolute_url),
            actor=actor_id,
            send_push=False,
        )


def _job_pre_save(sender, instance, **kwargs):
    if kwargs.get('raw'):
        return
    before = None
    if instance.pk:
        before = sender.objects.filter(pk=instance.pk).values(*SNAP_FIELDS).first()
    instance._job_events_before = before


def _job_post_save(sender, instance, created, **kwargs):
    if kwargs.get('raw'):
        return
    before = getattr(instance, '_job_events_before', None)
    after = _snapshot(instance)
    instance._job_events_before = after
    if before == after and not created:
        return
    actor_id = getattr(instance, 'updated_by_id', None) or getattr(instance, 'created_by_id', None)
    _field_events(instance, before or {}, after, actor_id)
    _office_events(instance, before, after, created, actor_id)


def _job_pre_delete(sender, instance, **kwargs):
    instance._job_events_field = _field_user_ids(_snapshot(instance))
    instance._job_events_label = (instance.display_number, instance.party.display_name)


def _job_post_delete(sender, instance, **kwargs):
    ids = getattr(instance, '_job_events_field', set())
    if not ids:
        return
    number, party = getattr(instance, '_job_events_label', (instance.number, ''))
    notify(
        ids,
        kind=Notification.KIND_JOB_CANCELLED,
        title=f'İş iptal edildi · {number}',
        body=party,
        url='',
        actor=None,
    )
    send_to_users(ids, 'field', obj_id=instance.pk)


def _sale_post_save(sender, instance, created, **kwargs):
    if not created or kwargs.get('raw') or not instance.number:
        return
    actor_id = getattr(instance, 'created_by_id', None)
    party = instance.party.display_name if instance.party_id else ''
    url = _url(instance.get_absolute_url)
    notify(
        [user.pk for user in users_with('can_sales')],
        kind=Notification.KIND_SALE_NEW,
        title=f'Yeni satış fişi · {instance.number}',
        body=party,
        url=url,
        actor=actor_id,
        send_push=False,
    )


def connect_job_events():
    from sales.models import Sale
    from service.models import Job

    pre_save.connect(_job_pre_save, sender=Job, dispatch_uid='job-events-pre-save')
    post_save.connect(_job_post_save, sender=Job, dispatch_uid='job-events-post-save')
    pre_delete.connect(_job_pre_delete, sender=Job, dispatch_uid='job-events-pre-delete')
    post_delete.connect(_job_post_delete, sender=Job, dispatch_uid='job-events-post-delete')
    post_save.connect(_sale_post_save, sender=Sale, dispatch_uid='job-events-sale-save')
