"""Scheduled notifications: evening field digest, daily maintenance heads-up."""

from datetime import timedelta

from django.utils import timezone

from .models import Notification
from .notifications import notify, prune, users_with

DIGEST_PREVIEW = 3


def field_digest(today=None) -> int:
    """'Yarın N işiniz var' for every technician with open jobs tomorrow."""
    from django.urls import reverse

    from crew.models import CrewMember
    from service.field_views import long_day
    from service.models import Job
    from service.services import field_visible_q

    today = today or timezone.localdate()
    tomorrow = today + timedelta(days=1)
    sent = 0
    members = CrewMember.objects.filter(is_active=True, user__isnull=False, user__is_active=True)
    for member in members.select_related('user'):
        jobs = list(
            Job.objects.filter(field_visible_q(member), date=tomorrow, status=Job.STATUS_OPEN)
            .select_related('party')
            .order_by('time', 'id')
        )
        if not jobs:
            continue
        bits = [
            f'{job.time.strftime("%H:%M")} {job.party.display_name}' if job.time else job.party.display_name
            for job in jobs[:DIGEST_PREVIEW]
        ]
        if len(jobs) > DIGEST_PREVIEW:
            bits.append(f'+{len(jobs) - DIGEST_PREVIEW}')
        rows = notify(
            [member.user_id],
            kind=Notification.KIND_DIGEST,
            title=f'Yarın {len(jobs)} işiniz var · {long_day(tomorrow)}',
            body=' · '.join(bits),
            url=reverse('portal-field-schedule'),
            dedupe_key=f'digest-{tomorrow.isoformat()}',
        )
        sent += len(rows)
    return sent


def maintenance_heads_up(today=None) -> int:
    """One bell entry per device care date coming due (or overdue) for service leads."""
    from django.urls import reverse

    from service.services import MAINTENANCE_WINDOW_DAYS, due_maintenance

    today = today or timezone.localdate()
    leads = [user.pk for user in users_with('can_service_lead')]
    if not leads:
        return 0
    url = reverse('portal-service-reminders')
    sent = 0
    for device in due_maintenance(today, MAINTENANCE_WINDOW_DAYS).select_related('party'):
        party = device.party.display_name if device.party_id else ''
        late = device.next_due < today
        rows = notify(
            leads,
            kind=Notification.KIND_MAINTENANCE,
            title=f'{"Bakım gecikti" if late else "Bakım yaklaşıyor"} · {party or device.name}',
            body=f'{device.name} · {device.next_due.strftime("%d.%m.%Y")}',
            url=url,
            dedupe_key=f'maint-{device.pk}-{device.next_due.isoformat()}',
            send_push=False,
        )
        sent += len(rows)
    return sent


def daily(today=None) -> dict:
    return {'maintenance': maintenance_heads_up(today), 'pruned': prune()}
