from datetime import timedelta

from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from accounts.http import crew_member_for, field_required, stock_scope
from accounts.portal import _wants_json
from accounts.toasts import queue_toast
from accounts.weather import get_weather
from stock.models import Product
from stock.services import SERVICE_CATEGORY_SLUG, mount_material_filter
from stock.views import _product_payload

from .models import Job, JobSoldPack, JobSoldUnit
from .services import (
    add_pack_photos,
    compact_job_number,
    delete_job_photo,
    delete_pack_photo,
    field_can_edit,
    field_can_view,
    field_mount_payload,
    field_visible_q,
    job_photo_response,
    mount_handover_gaps,
    save_field_job,
    sold_unit_groups,
    submit_field_job,
    unit_photo_response,
    week_start,
)
from .slip import build_job_slip_cpcl, build_job_slip_zpl, slip_context
from .views import TR_DOW, _fmt_day_label, _fmt_week_label, _job_lines_payload


def _ctx(**extra):
    extra.setdefault('weather', get_weather())
    extra.setdefault('field_board', True)
    return extra


def _sold_field_payload(job):
    if not job.sale_id:
        return {
            'sold_groups': [],
            'multi_packs': [],
            'multi_indoors': [],
            'show_multi_groups': False,
        }
    sold_groups = sold_unit_groups(job)
    multi_packs = [group['pack'] for group in sold_groups if group.get('kind') == 'multi']
    pack_ids = [pack.pk for pack in multi_packs]
    multi_indoors = []
    if pack_ids:
        multi_indoors = list(
            JobSoldUnit.objects.filter(job=job)
            .filter(Q(pack_id__in=pack_ids) | Q(pack__isnull=True))
            .select_related('product', 'pack')
            .order_by('id')
        )
    return {
        'sold_groups': sold_groups,
        'multi_packs': multi_packs,
        'multi_indoors': multi_indoors,
        'show_multi_groups': len(multi_packs) > 1 and bool(multi_indoors),
    }


def _field_week(*, member, today):
    week_from = week_start(today)
    week_to = week_from + timedelta(days=6)
    qs = Job.objects.none()
    if member:
        qs = (
            Job.objects.filter(
                field_visible_q(member),
                date__gte=week_from,
                date__lte=week_to,
                status=Job.STATUS_OPEN,
            )
            .select_related('party', 'assignee', 'sale')
            .order_by('date', 'time', 'id')
        )
    by_day = {}
    for item in qs:
        by_day.setdefault(item.date, []).append(item)
    rows = []
    for offset in range(7):
        day_key = week_from + timedelta(days=offset)
        rows.append({
            'date': day_key,
            'dow': TR_DOW[offset],
            'label': _fmt_day_label(day_key),
            'today': day_key == today,
            'past': day_key < today,
            'jobs': by_day.get(day_key, []),
        })
    tomorrow = today + timedelta(days=1)
    tomorrow_jobs = []
    if member:
        tomorrow_jobs = list(
            Job.objects.filter(
                field_visible_q(member),
                date=tomorrow,
                status=Job.STATUS_OPEN,
            )
            .select_related('party', 'assignee', 'sale')
            .order_by('time', 'id')
        )
    return {
        'week_rows': rows,
        'week_label': _fmt_week_label(week_from, week_to),
        'today_jobs': by_day.get(today, []),
        'tomorrow': tomorrow,
        'tomorrow_jobs': tomorrow_jobs,
    }


def _recent_done_jobs(member):
    if not member:
        return []
    return list(
        Job.objects.filter(
            assignee=member,
            status__in=(Job.STATUS_SUBMITTED, Job.STATUS_CLOSED),
        )
        .select_related('party', 'assignee', 'sale')
        .order_by(F('submitted_at').desc(nulls_last=True), '-updated_at', '-id')[:5]
    )


@field_required
def field_home(request: HttpRequest) -> HttpResponse:
    member = crew_member_for(request.user)
    today = timezone.localdate()
    pack = _field_week(member=member, today=today)
    return render(
        request,
        'portal/field_home.html',
        _ctx(
            member=member,
            today=today,
            recent_done=_recent_done_jobs(member),
            **pack,
        ),
    )


@field_required
def field_schedule(request: HttpRequest) -> HttpResponse:
    member = crew_member_for(request.user)
    today = timezone.localdate()
    pack = _field_week(member=member, today=today)
    return render(
        request,
        'portal/field_schedule.html',
        _ctx(
            member=member,
            today=today,
            **pack,
        ),
    )


def _load_field_job(request: HttpRequest, number: str) -> Job:
    job = get_object_or_404(
        Job.objects.select_related('party', 'device', 'sale', 'assignee', 'assignee__user', 'created_by'),
        number=compact_job_number(number),
    )
    if not field_can_view(job=job, user=request.user):
        raise Http404()
    return job


@field_required
@require_http_methods(['GET', 'POST'])
def field_job(request: HttpRequest, number: str) -> HttpResponse:
    job = _load_field_job(request, number)
    if request.method == 'GET' and (
        str(request.GET.get('unit', '')).strip() or str(request.GET.get('group', '')).strip()
    ):
        return unit_photo_response(
            job=job,
            raw_id=str(request.GET.get('unit', '')).strip(),
            photo_id=str(request.GET.get('photo', '')).strip(),
            pack=bool(str(request.GET.get('pack', '')).strip() or str(request.GET.get('zip', '')).strip()),
            group_id=str(request.GET.get('group', '')).strip(),
        )
    if request.method == 'GET' and str(request.GET.get('photo', '')).strip():
        return job_photo_response(job=job, photo_id=str(request.GET.get('photo', '')).strip())
    error = ''
    can_edit = field_can_edit(job=job, user=request.user)
    if request.method == 'POST':
        action = str(request.POST.get('action', '')).strip()
        if not can_edit:
            error = 'Bu iş teslim edildi veya size atanmadı.'
            if _wants_json(request):
                return JsonResponse({'ok': False, 'error': error}, status=400)
        else:
            try:
                if action == 'delete_photo':
                    delete_job_photo(job=job, post=request.POST)
                    queue_toast(request, 'Görsel silindi.')
                    return redirect(job.get_field_url())
                if action == 'delete_unit_photo':
                    delete_pack_photo(job=job, post=request.POST)
                    if _wants_json(request):
                        return JsonResponse({'ok': True})
                    queue_toast(request, 'Görsel silindi.')
                    return redirect(job.get_field_url())
                if action == 'unit_photo':
                    pack_id = str(request.POST.get('pack_id', '')).strip()
                    if not pack_id.isdigit():
                        raise ValueError('Cihaz seçin.')
                    pack = JobSoldPack.objects.filter(pk=int(pack_id), job=job).first()
                    if not pack:
                        raise ValueError('Cihaz bulunamadı.')
                    photos = add_pack_photos(job=job, pack=pack, files=request.FILES)
                    if _wants_json(request):
                        return JsonResponse({'ok': True, 'photos': photos})
                    queue_toast(request, 'Görsel kaydedildi.')
                    return redirect(job.get_field_url())
                if action == 'submit' and job.sale_id:
                    gaps = mount_handover_gaps(job)
                    if gaps:
                        raise ValueError(gaps[0])
                    job = submit_field_job(job=job, user=request.user)
                    queue_toast(request, 'İş teslim edildi.')
                    if _wants_json(request):
                        return JsonResponse({'ok': True, 'next': reverse('portal-field')})
                    return redirect('portal-field')
                job = save_field_job(user=request.user, job=job, post=request.POST, files=request.FILES)
                if job.is_submitted:
                    queue_toast(request, 'İş teslim edildi.')
                    if _wants_json(request):
                        return JsonResponse({'ok': True, 'next': reverse('portal-field')})
                    return redirect('portal-field')
                if job.sale_id and action == 'save':
                    gaps = mount_handover_gaps(job)
                    if gaps:
                        raise ValueError(gaps[0])
                    next_url = f'{job.get_field_url()}?summary=1'
                    queue_toast(request, 'Montaj fişi hazır.')
                    if _wants_json(request):
                        return JsonResponse({'ok': True, 'next': next_url})
                    return redirect(next_url)
                queue_toast(request, 'İş kaydedildi.')
                if _wants_json(request):
                    return JsonResponse({'ok': True, 'next': job.get_field_url()})
                return redirect(job.get_field_url())
            except ValueError as exc:
                error = str(exc)
                if _wants_json(request):
                    return JsonResponse({'ok': False, 'error': error}, status=400)
        job = Job.objects.select_related('party', 'device', 'sale', 'assignee').get(pk=job.pk)
        can_edit = field_can_edit(job=job, user=request.user)
    lines = list(job.lines.select_related('product'))
    photos = list(job.photos.all())
    sold = _sold_field_payload(job)
    show_summary = False
    if job.sale_id:
        gaps = mount_handover_gaps(job)
        want_summary = str(request.GET.get('summary', '')).strip() == '1'
        if job.is_submitted or (want_summary and not gaps):
            show_summary = True
        elif want_summary:
            return redirect(job.get_field_url())
    return render(
        request,
        'portal/field_job.html',
        _ctx(
            job=job,
            error=error,
            can_edit=can_edit,
            lines=lines,
            line_rows=_job_lines_payload(job, prices=False),
            mount_rows=field_mount_payload(job) if job.sale_id else [],
            photos=photos,
            from_sale=bool(job.sale_id),
            show_summary=show_summary,
            **sold,
        ),
    )


@field_required
@require_GET
def field_print(request: HttpRequest, number: str) -> HttpResponse:
    job = _load_field_job(request, number)
    fmt = str(request.GET.get('format', '')).strip().lower()
    if fmt in {'cpcl', 'zpl'}:
        payload = build_job_slip_zpl(job) if fmt == 'zpl' else build_job_slip_cpcl(job)
        response = HttpResponse(payload, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{job.number}.{fmt}"'
        return response
    return render(
        request,
        'portal/field_print.html',
        _ctx(**slip_context(job)),
    )


@field_required
@require_GET
def field_products(request: HttpRequest) -> JsonResponse:
    query = str(request.GET.get('q', '')).strip()
    try:
        page = max(1, int(request.GET.get('page', '1')))
    except (TypeError, ValueError):
        page = 1
    qs = Product.objects.filter(is_active=True, is_device=False).select_related('category')
    mount = str(request.GET.get('mount', '')).strip() in ('1', 'true', 'on')
    service = str(request.GET.get('service', '')).strip() in ('1', 'true', 'on')
    if mount:
        qs = qs.filter(mount_material_filter())
    elif service:
        qs = qs.filter(category__is_klima=False).exclude(category__slug=SERVICE_CATEGORY_SLUG)
    scope = stock_scope(request.user)
    if scope is not None and not service:
        qs = qs.filter(category__in=scope)
    for token in [item for item in query.split() if item]:
        qs = qs.filter(
            Q(name__icontains=token)
            | Q(sku__icontains=token)
            | Q(brand__icontains=token)
            | Q(category__name__icontains=token)
        )
    order = ('category__name', 'name') if service else ('name',)
    paginator = Paginator(qs.order_by(*order), 20)
    page_obj = paginator.get_page(page)
    results = []
    for item in page_obj.object_list:
        row = _product_payload(item)
        row['category'] = item.category.name if item.category_id else ''
        row.pop('stock', None)
        row.pop('price', None)
        row.pop('buy', None)
        results.append(row)
    return JsonResponse(
        {
            'ok': True,
            'results': results,
            'page': page_obj.number,
            'pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
        }
    )
