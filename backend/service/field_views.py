import re
from datetime import timedelta

from django.core.paginator import Paginator
from django.db.models import F, Q, Value
from django.db.models.functions import Replace
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from accounts.http import crew_member_for, field_required, stock_scope
from accounts.portal import _wants_json
from accounts.search import q_search
from accounts.toasts import queue_toast
from accounts.weather import get_weather
from stock.models import Product
from stock.services import SERVICE_CATEGORY_SLUG, mount_material_filter
from stock.views import _product_payload

from .models import Job, JobLine, JobSoldPack, JobSoldUnit
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
    return {
        'week_rows': rows,
        'week_label': _fmt_week_label(week_from, week_to),
        'today_jobs': by_day.get(today, []),
    }


UPCOMING_DAYS = 14
UPCOMING_LIMIT = 8
TR_DOW_LONG = ('Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar')
TR_MONTHS = (
    'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
    'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık',
)


def relative_day(day, today) -> str:
    """'Bugün', 'Yarın', '3 gün sonra', '2 gün geçti'."""
    delta = (day - today).days
    if delta == 0:
        return 'Bugün'
    if delta == 1:
        return 'Yarın'
    if delta > 1:
        return f'{delta} gün sonra'
    return f'{-delta} gün geçti'


def long_day(day) -> str:
    return f'{TR_DOW_LONG[day.weekday()]}, {day.day} {TR_MONTHS[day.month - 1]}'


def _job_place(job) -> str:
    sale = getattr(job, 'sale', None)
    if sale is not None and sale.mount_place_summary:
        return sale.mount_place_summary
    party = job.party
    loc = ' / '.join(p for p in ((party.district or '').strip(), (party.city or '').strip()) if p)
    address = (party.address or '').strip()
    return f'{loc} · {address}' if loc and address else (loc or address)


def _job_phone(job) -> str:
    sale = getattr(job, 'sale', None)
    phone = (getattr(sale, 'mount_phone', '') or '').strip() if sale is not None else ''
    return phone or (job.party.phone or '').strip()


def field_card(job, today) -> dict:
    """Everything a field job card shows (home list, upcoming list)."""
    from urllib.parse import quote

    place = _job_place(job)
    summary = job.device_summary
    return {
        'job': job,
        'kind': job.kind_label,
        'kind_class': 'is-mount' if job.is_mount else 'is-service',
        'device': '' if summary == '—' else summary,
        'place': place,
        'phone': _job_phone(job),
        'maps_url': f'https://www.google.com/maps/dir/?api=1&destination={quote(place)}' if place else '',
        'when': relative_day(job.date, today),
        'dow': TR_DOW[job.date.weekday()],
    }


def _field_upcoming(member, today):
    if not member:
        return []
    qs = (
        Job.objects.filter(
            field_visible_q(member),
            date__gt=today,
            date__lte=today + timedelta(days=UPCOMING_DAYS),
            status=Job.STATUS_OPEN,
        )
        .select_related('party', 'assignee', 'sale', 'device')
        .prefetch_related('sold_packs')
        .order_by('date', 'time', 'id')[:UPCOMING_LIMIT]
    )
    return [field_card(job, today) for job in qs]


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
    today_ids = [job.pk for job in pack['today_jobs']]
    today_cards = [
        field_card(job, today)
        for job in Job.objects.filter(pk__in=today_ids)
        .select_related('party', 'assignee', 'sale', 'device')
        .prefetch_related('sold_packs')
        .order_by('time', 'id')
    ]
    upcoming = _field_upcoming(member, today)
    return render(
        request,
        'portal/field_home.html',
        _ctx(
            member=member,
            today=today,
            today_label=long_day(today),
            today_cards=today_cards,
            upcoming=upcoming,
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
            card=field_card(job, timezone.localdate()),
            day_label=long_day(job.date),
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
        qs = qs.filter(mount_material_filter() | Q(category__slug=SERVICE_CATEGORY_SLUG))
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
    paginator = Paginator(qs.order_by(*order), 100)
    page_obj = paginator.get_page(page)
    results = []
    for item in page_obj.object_list:
        row = _product_payload(item)
        row['category'] = item.category.name if item.category_id else ''
        row['is_service'] = bool(item.category_id and item.category.slug == SERVICE_CATEGORY_SLUG)
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


CUSTOMER_PAGE_SIZE = 20


CUSTOMER_PHONE_MIN_DIGITS = 4


def _phone_digits(field: str):
    expr = F(field)
    for ch in (' ', '(', ')', '-', '+', '.'):
        expr = Replace(expr, Value(ch), Value(''))
    return expr


def _query_phone_digits(query: str) -> str:
    digits = re.sub(r'\D', '', query)
    if len(digits) > 10 and digits.startswith('90'):
        digits = digits[2:]
    return digits.lstrip('0')


def field_customer_q(query: str) -> Q:
    q = Q()
    for token in query.split():
        q &= q_search(
            token,
            'party__first_name',
            'party__last_name',
            'party__company_name',
            'mount_contact_name',
            'service_job__sold_units__serial',
            'service_job__sold_units__outdoor_serial',
            'service_job__sold_packs__outdoor_serial',
        )
    return q


def field_customer_sale_ids(query: str):
    from sales.models import Sale

    q = field_customer_q(query)
    digits = _query_phone_digits(query)
    if len(digits) >= CUSTOMER_PHONE_MIN_DIGITS:
        q |= Q(party_phone_digits__contains=digits) | Q(mount_phone_digits__contains=digits)
    return (
        Sale.objects.annotate(
            party_phone_digits=_phone_digits('party__phone'),
            mount_phone_digits=_phone_digits('mount_phone'),
        )
        .filter(q)
        .values('pk')
    )


def _sale_mount_job(sale):
    try:
        return sale.service_job
    except Job.DoesNotExist:
        return None


def _device_lines(sale) -> list:
    return [line for line in sale.lines.all() if line.product_id and line.product.is_device]


def _customer_card(sale) -> dict:
    party = sale.party
    devices = _device_lines(sale)
    summary = devices[0].product.display_name if devices else ''
    if len(devices) > 1:
        summary += f' +{len(devices) - 1}'
    place = sale.mount_place_summary
    if not place:
        place = ' / '.join(p for p in ((party.district or '').strip(), (party.city or '').strip()) if p)
    job = _sale_mount_job(sale)
    return {
        'sale': sale,
        'party': party,
        'place': place,
        'devices': summary,
        'mount_on': job.date if job else None,
        'url': reverse('portal-field-customer', kwargs={'number': sale.number}),
    }


@field_required
@require_GET
def field_customers(request: HttpRequest) -> HttpResponse:
    from django.db.models.functions import Coalesce

    from sales.models import Sale

    from .views import _page_nav

    query = str(request.GET.get('q', '')).strip()
    if not query:
        return render(request, 'portal/field_customers.html', _ctx(query='', cards=[]))
    qs = (
        Sale.objects.filter(work_type=Sale.WORK_DEVICE, pk__in=field_customer_sale_ids(query))
        .select_related('party', 'service_job')
        .prefetch_related('lines__product')
        .annotate(mount_on=Coalesce('service_job__date', 'date'))
        .order_by('-mount_on', '-id')
    )
    paginator = Paginator(qs, CUSTOMER_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))
    ctx = _ctx(
        query=query,
        cards=[_customer_card(sale) for sale in page_obj.object_list],
        **_page_nav(paginator, page_obj, {'q': query}),
    )
    return render(request, 'portal/field_customers.html', ctx)


def _photo_param(request, key: str) -> str:
    return str(request.GET.get(key, '')).strip()


@field_required
@require_GET
def field_customer(request: HttpRequest, number: str) -> HttpResponse:
    from sales.models import Sale

    sale = get_object_or_404(Sale.objects.select_related('party'), number=number, work_type=Sale.WORK_DEVICE)
    job = Job.objects.filter(sale=sale).select_related('assignee').first()
    photo_id = _photo_param(request, 'photo')
    if photo_id and _photo_param(request, 'job'):
        raw = _photo_param(request, 'job')
        other = Job.objects.filter(pk=int(raw), party=sale.party).first() if raw.isdigit() else None
        if other is None:
            raise Http404()
        return job_photo_response(job=other, photo_id=photo_id)
    if _photo_param(request, 'unit') or _photo_param(request, 'group'):
        if job is None:
            raise Http404()
        return unit_photo_response(
            job=job,
            raw_id=_photo_param(request, 'unit'),
            photo_id=photo_id,
            group_id=_photo_param(request, 'group'),
        )
    if photo_id:
        if job is None:
            raise Http404()
        return job_photo_response(job=job, photo_id=photo_id)

    base = reverse('portal-field-customer', kwargs={'number': sale.number})
    groups = []
    job_shots = []
    if job is not None:
        packs = (
            JobSoldPack.objects.filter(job=job)
            .select_related('outdoor_product')
            .prefetch_related('units', 'photos')
            .order_by('sort', 'id')
        )
        for pack in packs:
            units = list(pack.units.all())
            if pack.kind == JobSoldPack.KIND_MULTI and not units:
                continue
            groups.append({
                'pack': pack,
                'units': units,
                'shots': [f'{base}?group={pack.pk}&photo={shot.pk}' for shot in pack.photo_items if shot.image],
            })
        job_shots = [f'{base}?photo={shot.pk}' for shot in job.photos.all() if shot.image]

    history = []
    party_jobs = (
        Job.objects.filter(party=sale.party)
        .select_related('assignee')
        .prefetch_related('lines__product', 'photos')
        .order_by('-date', '-id')
    )
    for item in party_jobs:
        works = [
            line.description or (line.product.name if line.product_id else '')
            for line in item.lines.all()
            if line.kind == JobLine.KIND_LABOR
        ]
        history.append({
            'job': item,
            'works': [work for work in works if work],
            'url': item.get_field_url() if field_can_view(job=item, user=request.user) else '',
            'shots': [] if item.pk == getattr(job, 'pk', None) else [
                f'{base}?job={item.pk}&photo={shot.pk}' for shot in item.photos.all() if shot.image
            ],
        })

    return render(
        request,
        'portal/field_customer.html',
        _ctx(
            sale=sale,
            party=sale.party,
            mount_job=job,
            groups=groups,
            job_shots=job_shots,
            device_lines=_device_lines(sale),
            history=history,
            card=_customer_card(sale),
        ),
    )
