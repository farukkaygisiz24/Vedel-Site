from calendar import monthrange
from datetime import date, timedelta
from itertools import groupby
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Count, F, Max, Min, Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from accounts.http import crew_member_for, role_required
from accounts.models import Customer
from accounts.portal import _wants_json
from accounts.search import q_search
from accounts.toasts import queue_toast
from accounts.weather import get_weather
from crew.models import CrewMember
from sales.models import Party, Payment
from sales.services import add_job_payment, delete_payment
from stock.models import Product
from stock.services import SERVICE_CATEGORY_SLUG

from .models import Device, Job, JobLine
from .services import (
    DAY_CAP,
    SERVICE_HOUR_LABELS,
    _resolve_assignment,
    _resolve_device,
    adjust_closed_job,
    assignment_form_values,
    compact_job_number,
    confirm_job,
    delete_job,
    field_visible_q,
    month_load_payload,
    parse_service_time,
    parse_year_month,
    party_device_choices,
    sale_line_is_device,
    save_field_job,
    save_job,
    sold_unit_groups,
    unassigned_sold_units,
    unit_photo_response,
    week_start,
)

JOB_PAGE_SIZE = 20
REMINDER_WINDOW_DAYS = 14
TR_MONTHS = [
    'Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz',
    'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara',
]
TR_MONTH_FULL = [
    'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
    'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık',
]
TR_DOW = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']


def _ctx(**extra):
    extra.setdefault('weather', get_weather())
    extra.setdefault('vat_choices', Job.VAT_CHOICES)
    extra.setdefault('interval_choices', Device.INTERVAL_CHOICES)
    return extra


def _service_board_url(job: Job) -> str:
    return f"{reverse('portal-service')}?day={job.date.isoformat()}"


def _querystring(values, page=None):
    data = {}
    for key, val in values.items():
        text = str(val or '').strip()
        if text:
            data[key] = text
    if page:
        try:
            page_no = int(page)
        except (TypeError, ValueError):
            page_no = 1
        if page_no > 1:
            data['page'] = str(page_no)
    encoded = urlencode(data)
    return f'?{encoded}' if encoded else '?'


def _page_nav(paginator, page_obj, filters):
    page_links = []
    for num in paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1):
        if num == paginator.ELLIPSIS:
            page_links.append({'label': '…', 'href': '', 'on': False, 'gap': True})
        else:
            page_links.append({
                'label': str(num),
                'href': _querystring(filters, page=num),
                'on': num == page_obj.number,
                'gap': False,
            })
    return {
        'page_obj': page_obj,
        'paginator': paginator,
        'page_links': page_links,
        'prev_href': _querystring(filters, page=page_obj.previous_page_number()) if page_obj.has_previous() else '',
        'next_href': _querystring(filters, page=page_obj.next_page_number()) if page_obj.has_next() else '',
    }


def _fmt_day_label(when: date) -> str:
    return f'{when.day} {TR_MONTHS[when.month - 1]} {when.year}'


def _slot_ask(job: Job) -> str:
    day = f'{job.date.day} {TR_MONTH_FULL[job.date.month - 1]} {job.date.year}'
    if job.time:
        return f'{day} saat {job.time.strftime("%H.%M")} için randevu ayrılmıştır. Onaylıyor musun?'
    return f'{day} için randevu ayrılmıştır. Onaylıyor musun?'


def _fmt_week_label(start: date, end: date) -> str:
    if start.month == end.month and start.year == end.year:
        return f'{start.day}–{end.day} {TR_MONTHS[end.month - 1]} {end.year}'
    if start.year == end.year:
        return (
            f'{start.day} {TR_MONTHS[start.month - 1]} – '
            f'{end.day} {TR_MONTHS[end.month - 1]} {end.year}'
        )
    return f'{_fmt_day_label(start)} – {_fmt_day_label(end)}'


def _parse_day(raw) -> date:
    today = timezone.localdate()
    text = str(raw or '').strip()
    if text:
        try:
            return date.fromisoformat(text)
        except ValueError:
            pass
    return today


def _shift_month(view: date, delta: int) -> date:
    month = view.month - 1 + delta
    year = view.year + month // 12
    month = month % 12 + 1
    return date(year, month, 1)


def _day_href(day: date, month: date | None = None) -> str:
    data = {'day': day.isoformat()}
    if month:
        data['month'] = f'{month.year:04d}-{month.month:02d}'
    return _querystring(data)


def _is_tech(user) -> bool:
    return getattr(user, 'can_service_field', False) and not getattr(user, 'can_service_lead', False)


def _visible_jobs(user):
    qs = Job.objects.all()
    if getattr(user, 'can_service_lead', False) or getattr(user, 'is_superuser', False):
        return qs
    member = crew_member_for(user)
    if getattr(user, 'can_service_field', False) and member:
        return qs.filter(field_visible_q(member)).exclude(status=Job.STATUS_PENDING)
    return qs.none()


def _week_pack(today: date, jobs_qs=None) -> dict:
    week_from = week_start(today)
    week_to = week_from + timedelta(days=6)
    source = jobs_qs if jobs_qs is not None else Job.objects.all()
    week_qs = (
        source.filter(
            date__gte=week_from,
            date__lte=week_to,
            status__in=[Job.STATUS_OPEN, Job.STATUS_SUBMITTED, Job.STATUS_CLOSED],
        )
        .select_related('party', 'assignee', 'sale')
        .order_by('date', 'time', 'id')
    )
    week_by_day = {}
    for item in week_qs:
        week_by_day.setdefault(item.date, []).append(item)
    week_rows = []
    for offset in range(7):
        day_key = week_from + timedelta(days=offset)
        week_rows.append({
            'date': day_key,
            'dow': TR_DOW[offset],
            'label': _fmt_day_label(day_key),
            'today': day_key == today,
            'past': day_key < today,
            'jobs': week_by_day.get(day_key, []),
        })
    return {
        'week_rows': week_rows,
        'week_label': _fmt_week_label(week_from, week_to),
    }


def _month_browse(*, view: date, chosen: date, today: date, jobs_qs=None) -> dict:
    first = date(view.year, view.month, 1)
    grid_start = first - timedelta(days=first.weekday())
    grid_end = grid_start + timedelta(days=41)
    count_from = max(grid_start, today)
    source = jobs_qs if jobs_qs is not None else Job.objects.all()
    counts = {}
    for when in (
        source.filter(
            date__gte=count_from,
            date__lte=grid_end,
            status=Job.STATUS_OPEN,
        ).values_list('date', flat=True)
    ):
        counts[when] = counts.get(when, 0) + 1
    if chosen >= today:
        jobs = (
            source.filter(date=chosen, status=Job.STATUS_OPEN)
            .select_related('party', 'device', 'assignee', 'created_by', 'sale')
            .order_by('time', 'id')
        )
        empty_copy = 'Bugün onaylanmış iş yok.' if chosen == today else 'Bu güne onaylanmış iş yok.'
    else:
        jobs = Job.objects.none()
        empty_copy = 'Kapanmamış işler gidilmeyenlerde. Yeni gün seçip güne alın.'
    month_end = date(view.year, view.month, monthrange(view.year, view.month)[1])
    month_from = max(first, today)
    month_qs = (
        source.filter(
            date__gte=month_from,
            date__lte=month_end,
            status=Job.STATUS_OPEN,
        )
        .select_related('party', 'assignee', 'sale')
        .order_by('date', 'time', 'id')
    )
    open_by_day = {}
    for day_key, items in groupby(month_qs, key=lambda item: item.date):
        open_by_day[day_key] = list(items)
    assign_day = chosen if chosen >= today else today
    day_panel = {'today': today.isoformat(), 'days': {}}
    cursor = first
    while cursor <= month_end:
        if cursor < today:
            panel_jobs = []
            panel_empty = 'Kapanmamış işler gidilmeyenlerde. Yeni gün seçip güne alın.'
        else:
            panel_jobs = [_browse_job(item) for item in open_by_day.get(cursor, ())]
            panel_empty = (
                'Bugün onaylanmış iş yok.'
                if cursor == today
                else 'Bu güne onaylanmış iş yok.'
            )
        day_panel['days'][cursor.isoformat()] = {
            'label': _fmt_day_label(cursor),
            'empty': panel_empty,
            'jobs': panel_jobs,
        }
        cursor += timedelta(days=1)
    return {
        'jobs': jobs,
        'empty_copy': empty_copy,
        'chosen_day': chosen,
        'chosen_label': _fmt_day_label(chosen),
        'today': today,
        'assign_day': assign_day,
        'assign_label': _fmt_day_label(assign_day),
        'cal_month_label': f'{TR_MONTH_FULL[view.month - 1]} {view.year}',
        'cal_cells': _cal_cells(view, chosen, today, counts),
        'cal_prev': _day_href(chosen, _shift_month(view, -1)),
        'cal_next': _day_href(chosen, _shift_month(view, 1)),
        'day_panel': day_panel,
    }


def _sold_items(job: Job) -> list[dict]:
    if not job.sale_id:
        return []
    rows = []
    for line in job.sale.lines.select_related('product', 'product__outdoor', 'product__category'):
        if not sale_line_is_device(line, job.sale):
            continue
        product = line.product
        if product:
            brand = (product.brand or '').strip() or '—'
            model = (product.name or '').strip() or '—'
            outdoor = ''
            if product.outdoor_id:
                outdoor = (product.outdoor.name or '').strip()
            if not outdoor:
                outdoor = (product.outdoor_name or '').strip()
        else:
            brand = '—'
            model = (line.description or '').strip() or 'Kalem'
            outdoor = ''
        rows.append({'brand': brand, 'model': model, 'qty': line.qty, 'outdoor': outdoor})
    return rows


def _browse_job(item: Job) -> dict:
    return {
        'url': item.get_absolute_url(),
        'time': item.time.strftime('%H:%M') if item.time else '',
        'party': item.party.display_name,
        'number': item.display_number,
        'kind': item.kind_label,
        'assignee': item.assignee_label,
    }


def _cal_cells(view: date, chosen: date, today: date, counts: dict) -> list[dict]:
    first = date(view.year, view.month, 1)
    start = first - timedelta(days=first.weekday())
    cells = []
    for offset in range(42):
        cell = start + timedelta(days=offset)
        count = counts.get(cell, 0)
        cells.append({
            'iso': cell.isoformat(),
            'day': cell.day,
            'href': _day_href(cell),
            'muted': cell.month != view.month,
            'today': cell == today,
            'on': cell == chosen,
            'count': count,
            'busy': 0 < count < DAY_CAP,
            'full': count >= DAY_CAP,
        })
    return cells


def _job_lines_payload(job: Job, *, prices: bool = True) -> list[dict]:
    rows = []
    for line in job.lines.select_related('product', 'product__category'):
        row = {
            'kind': line.kind,
            'product_id': line.product_id or '',
            'product_name': line.product.display_name if line.product_id else '',
            'sku': line.product.sku if line.product_id else '',
            'unit': line.product.unit if line.product_id else '',
            'category': line.product.category.name if line.product_id and line.product.category_id else '',
            'stock': str(line.product.stock_qty) if line.product_id else '',
            'description': line.description,
            'qty': str(line.qty),
            'vat_rate': str(line.vat_rate),
        }
        if prices:
            row['unit_price'] = str(line.unit_price)
            row['cost_price'] = str(line.cost_price)
        rows.append(row)
    return rows


@role_required(Customer.ROLE_SERVICE_LEAD)
@require_GET
def device_list_json(request: HttpRequest) -> HttpResponse:
    party_id = str(request.GET.get('party', '')).strip()
    if not party_id:
        return JsonResponse({'ok': True, 'results': []})
    if not party_id.isdigit():
        return JsonResponse({'ok': True, 'results': []})
    party = Party.objects.filter(pk=int(party_id)).first()
    if not party:
        return JsonResponse({'ok': True, 'results': []})
    return JsonResponse({'ok': True, 'results': party_device_choices(party)})


@role_required(Customer.ROLE_SERVICE, Customer.ROLE_SERVICE_LEAD)
def schedule(request: HttpRequest) -> HttpResponse:
    visible = _visible_jobs(request.user)
    tech_mode = _is_tech(request.user)
    if _wants_json(request):
        year, month = parse_year_month(request.GET.get('month'))
        return JsonResponse(month_load_payload(year, month, qs=visible if tech_mode else None))
    today = timezone.localdate()
    chosen = _parse_day(request.GET.get('day'))
    year, month = parse_year_month(request.GET.get('month'), fallback=chosen)
    view = date(year, month, 1)
    related = ('party', 'sale', 'device', 'assignee', 'created_by')
    if tech_mode:
        waiting = Job.objects.none()
        missed = Job.objects.none()
        submitted = Job.objects.none()
    else:
        waiting = (
            Job.objects.filter(status=Job.STATUS_PENDING, date__gte=today)
            .select_related(*related)
            .order_by('date', 'time', 'id')
        )
        missed = (
            Job.objects.filter(
                Q(status=Job.STATUS_PENDING, date__lt=today)
                | Q(status=Job.STATUS_OPEN, date__lt=today)
            )
            .select_related(*related)
            .order_by('date', 'time', 'id')
        )
        submitted = (
            visible.filter(status=Job.STATUS_SUBMITTED)
            .select_related(*related)
            .order_by('-submitted_at', 'date', 'time', 'id')
        )
    return render(
        request,
        'portal/service_schedule.html',
        _ctx(
            waiting=waiting,
            missed=missed,
            submitted=submitted,
            tech_mode=tech_mode,
            **_week_pack(today, visible),
            **_month_browse(view=view, chosen=chosen, today=today, jobs_qs=visible),
        ),
    )


@role_required(Customer.ROLE_SERVICE, Customer.ROLE_SERVICE_LEAD)
def job_list(request: HttpRequest) -> HttpResponse:
    query = str(request.GET.get('q', '')).strip()
    status = str(request.GET.get('status', '')).strip()
    kind = str(request.GET.get('kind', '')).strip()
    qs = (
        _visible_jobs(request.user)
        .select_related('party', 'device', 'assignee', 'created_by', 'sale')
        .prefetch_related('sold_packs')
    )
    if query:
        qs = qs.filter(
            models_q(query)
        )
    if status in {Job.STATUS_PENDING, Job.STATUS_OPEN, Job.STATUS_SUBMITTED, Job.STATUS_CLOSED}:
        qs = qs.filter(status=status)
    else:
        status = ''
    if kind == 'mount':
        qs = qs.filter(sale_id__isnull=False)
    elif kind == 'service':
        qs = qs.filter(sale_id__isnull=True)
    else:
        kind = ''
    try:
        page = max(1, int(request.GET.get('page', '1')))
    except (TypeError, ValueError):
        page = 1
    paginator = Paginator(qs, JOB_PAGE_SIZE)
    page_obj = paginator.get_page(page)
    filters = {'q': query, 'status': status, 'kind': kind}
    if not page_obj.object_list:
        if query or status or kind:
            empty_copy = 'Bu süzgeçte iş yok.'
        elif _is_tech(request.user):
            empty_copy = 'Size atanan iş yok.'
        else:
            empty_copy = 'Henüz iş yok. Yeni iş ile ilk kaydı açın.'
    else:
        empty_copy = ''
    return render(
        request,
        'portal/service_jobs.html',
        _ctx(
            jobs=page_obj.object_list,
            query=query,
            status=status,
            kind=kind,
            empty_copy=empty_copy,
            tech_mode=_is_tech(request.user),
            **_page_nav(paginator, page_obj, filters),
        ),
    )


@role_required(Customer.ROLE_SERVICE_LEAD)
def client_list(request: HttpRequest) -> HttpResponse:
    query = str(request.GET.get('q', '')).strip()
    qs = Party.objects.annotate(
        device_count=Count('devices', distinct=True),
        job_count=Count('service_jobs', distinct=True),
        last_job_on=Max('service_jobs__date'),
        next_care=Min('devices__next_due'),
    )
    if query:
        qs = qs.filter(client_q(query))
    qs = qs.order_by(F('last_job_on').desc(nulls_last=True), '-id')
    try:
        page = max(1, int(request.GET.get('page', '1')))
    except (TypeError, ValueError):
        page = 1
    paginator = Paginator(qs, JOB_PAGE_SIZE)
    page_obj = paginator.get_page(page)
    filters = {'q': query}
    if not page_obj.object_list:
        empty_copy = 'Bu süzgeçte müşteri yok.' if query else 'Henüz müşteri yok. Yeni müşteri ile ilk kaydı açın.'
    else:
        empty_copy = ''
    return render(
        request,
        'portal/service_clients.html',
        _ctx(
            parties=page_obj.object_list,
            query=query,
            empty_copy=empty_copy,
            today=timezone.localdate(),
            **_page_nav(paginator, page_obj, filters),
        ),
    )


def client_q(query: str):
    q = Q()
    for token in query.split():
        q &= q_search(
            token,
            'first_name',
            'last_name',
            'company_name',
            'phone',
            'phone2',
            'number',
            'address',
            'city',
            'district',
        )
    return q


def models_q(query: str):
    q = Q()
    for token in query.split():
        q &= q_search(
            token,
            'number',
            'party__first_name',
            'party__last_name',
            'party__company_name',
            'party__number',
            'party__phone',
            'device__name',
            'device__place',
            'sale__number',
        )
    return q


def _job_form_context(request: HttpRequest, job: Job | None = None, error=''):
    party = job.party if job else None
    device = job.device if job else None
    party_id = str(request.GET.get('party', '')).strip()
    device_id = str(request.GET.get('device', '')).strip()
    if not party and party_id.isdigit():
        party = Party.objects.filter(pk=int(party_id)).first()
    if party and not device and device_id.isdigit():
        device = Device.objects.filter(pk=int(device_id), party=party).first()
    registry = list(Device.objects.filter(party=party)) if party else []
    devices = party_device_choices(party) if party else []
    lines = _job_lines_payload(job) if job else []
    today = timezone.localdate()
    seed = job.date if job else today
    sold_groups = sold_unit_groups(job) if job and job.sale_id else []
    unassigned_units = unassigned_sold_units(job) if job and job.sale_id else []
    multi_packs = [group['pack'] for group in sold_groups if group.get('kind') == 'multi']
    multi_indoors = list(unassigned_units)
    for group in sold_groups:
        if group.get('kind') == 'multi':
            multi_indoors.extend(group['units'])
    multi_indoors.sort(key=lambda item: item.pk)
    if job and job.sale_id:
        device_mode = 'none'
    else:
        device_mode = 'existing' if (device or devices) else 'none'
    office_close = bool(job and job.is_submitted)
    work_choices = list(
        Product.objects.filter(is_active=True, category__slug=SERVICE_CATEGORY_SLUG).order_by('sku')
    )
    work_id = ''
    work_name = ''
    if job:
        work_line = (
            job.lines.filter(kind=JobLine.KIND_LABOR, product__category__slug=SERVICE_CATEGORY_SLUG)
            .select_related('product')
            .first()
        )
        if work_line and work_line.product_id:
            work_id = str(work_line.product_id)
            work_name = work_line.product.name
    assignee_id, assignee_name = assignment_form_values(job)
    return {
        'job': job,
        'error': error,
        'office_close': office_close,
        'initial_party': {
            'id': party.pk,
            'name': party.display_name,
            'kind_label': party.get_kind_display(),
            'phone': party.phone,
            'number': party.number,
        } if party else None,
        'initial_device_id': str(device.pk) if device else '',
        'devices': devices,
        'initial_lines': lines,
        'notes': job.notes if job else '',
        'vat_mode': job.vat_mode if job else Job.VAT_NONE,
        'device_interval': device.interval_months if device else 12,
        'device_place': device.place if device else '',
        'device_mode': device_mode,
        'assignee_id': assignee_id,
        'assignee_name': assignee_name,
        'work_id': work_id,
        'work_name': work_name,
        'work_choices': work_choices,
        'crew': list(CrewMember.objects.filter(is_active=True)),
        'sold_items': _sold_items(job) if job else [],
        'sold_groups': sold_groups,
        'unassigned_units': unassigned_units,
        'multi_packs': multi_packs,
        'multi_indoors': multi_indoors,
        'party_devices': registry,
        'warranty_missing': bool(sold_groups or unassigned_units) and (
            bool(unassigned_units)
            or any(not unit.serial for group in sold_groups for unit in group['units'])
            or any(
                group['pack'].outdoor_name and not group['pack'].outdoor_serial
                for group in sold_groups
                if group.get('pack')
            )
        ),
        'from_sale': bool(job and job.sale_id),
        'photos': list(job.photos.all()) if job else [],
        'service_hours': SERVICE_HOUR_LABELS,
        'job_time': job.time.strftime('%H:%M') if job and job.time else '',
        'job_date': seed.isoformat(),
        'service_load': month_load_payload(seed.year, seed.month),
        'today': today,
        'tech_mode': _is_tech(request.user),
    }


@role_required(Customer.ROLE_SERVICE_LEAD)
@require_http_methods(['GET', 'POST'])
def job_new(request: HttpRequest) -> HttpResponse:
    error = ''
    if request.method == 'POST':
        try:
            job = save_job(user=request.user, post=request.POST)
            if job.status == Job.STATUS_CLOSED:
                text = queue_toast(request, 'İş kapatıldı.')
                next_url = job.get_absolute_url()
            else:
                text = queue_toast(request, 'Servis işi kaydedildi.')
                next_url = _service_board_url(job)
            if _wants_json(request):
                return JsonResponse(
                    {'ok': True, 'url': next_url, 'toast': text, 'closed': job.status == Job.STATUS_CLOSED}
                )
            return redirect(next_url)
        except (ValueError, Party.DoesNotExist, Product.DoesNotExist) as exc:
            error = str(exc)
            if _wants_json(request):
                return JsonResponse({'ok': False, 'error': error}, status=400)
    return render(
        request,
        'portal/service_job_form.html',
        _ctx(**_job_form_context(request, error=error)),
    )


@role_required(Customer.ROLE_SERVICE, Customer.ROLE_SERVICE_LEAD)
@require_http_methods(['GET', 'POST'])
def job_detail(request: HttpRequest, number: str) -> HttpResponse:
    job = get_object_or_404(
        Job.objects.select_related('party', 'device', 'sale', 'assignee', 'created_by'),
        number=compact_job_number(number),
    )
    tech_mode = _is_tech(request.user)
    if tech_mode and not _visible_jobs(request.user).filter(pk=job.pk).exists():
        return redirect('portal-service-jobs')
    error = ''
    pay_open = False
    pay_amount = ''
    pay_method = ''
    pay_date = timezone.localdate().isoformat()
    card_holder = ''
    card_installments = ''
    transfer_sender = ''
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
    if request.method == 'POST':
        action = str(request.POST.get('action', '')).strip()
        try:
            if tech_mode and action in {'delete', 'confirm', 'close', 'payment', 'delete_payment', 'adjust'}:
                raise ValueError('Bu işlem için yetkiniz yok.')
            if tech_mode:
                job = save_field_job(user=request.user, job=job, post=request.POST, files=request.FILES)
                queue_toast(request, 'Servis işi güncellendi.')
                return redirect(job.get_absolute_url())
            if action == 'payment':
                add_job_payment(job=job, user=request.user, post=request.POST)
                queue_toast(request, 'Ödeme kaydedildi.')
                return redirect(job.get_absolute_url())
            if action == 'delete_payment':
                delete_payment(user=request.user, post=request.POST, job=job)
                queue_toast(request, 'Tahsilat silindi.')
                if _wants_json(request):
                    return JsonResponse(
                        {
                            'ok': True,
                            'url': job.get_absolute_url(),
                            'toast': 'Tahsilat silindi.',
                        }
                    )
                return redirect(job.get_absolute_url())
            if action == 'adjust':
                job = adjust_closed_job(job=job, user=request.user, post=request.POST)
                queue_toast(request, 'Ödeme detayları güncellendi.')
                return redirect(job.get_absolute_url())
            if action == 'delete':
                delete_job(job=job, user=request.user)
                queue_toast(request, 'İş silindi.')
                return redirect('portal-service-jobs')
            if action == 'confirm':
                when = None
                clock = None
                raw_day = str(request.POST.get('service_date', '')).strip()
                if raw_day:
                    try:
                        when = date.fromisoformat(raw_day)
                    except ValueError as exc:
                        raise ValueError('Servis günü geçersiz.') from exc
                raw_clock = str(request.POST.get('service_time', '')).strip()
                if raw_clock:
                    clock = parse_service_time(raw_clock)
                elif job.time:
                    clock = job.time
                else:
                    raise ValueError('Servis saati seçin.')
                assignee, assign_all = _resolve_assignment(request.POST)
                if not assignee and not assign_all:
                    raise ValueError('Personel seçin.')
                confirm_job(
                    job=job,
                    user=request.user,
                    when=when,
                    clock=clock,
                    assignee=assignee,
                    assign_all=assign_all,
                )
                next_url = f"{reverse('portal-service')}?day={job.date.isoformat()}"
                text = queue_toast(request, 'Gün kabul edildi.')
                if _wants_json(request):
                    return JsonResponse({'ok': True, 'url': next_url, 'toast': text})
                return redirect(next_url)
            if job.is_waiting:
                raise ValueError('Bekleyen iş önce güne alınır.')
            if not job.is_open and not job.is_submitted:
                raise ValueError('Kapalı iş düzenlenemez.')
            job = save_job(user=request.user, post=request.POST, files=request.FILES, job=job)
            if job.status == Job.STATUS_CLOSED:
                text = queue_toast(request, 'İş kapatıldı.')
                next_url = job.get_absolute_url()
            else:
                text = queue_toast(request, 'Servis işi güncellendi.')
                next_url = _service_board_url(job)
            if action == 'close' and _wants_json(request):
                return JsonResponse(
                    {
                        'ok': True,
                        'url': next_url,
                        'toast': text,
                        'closed': job.status == Job.STATUS_CLOSED,
                    }
                )
            return redirect(next_url)
        except ValueError as exc:
            error = str(exc)
            if action in {'confirm', 'close', 'delete_payment'} and _wants_json(request):
                return JsonResponse({'ok': False, 'error': error}, status=400)
            if action == 'payment':
                pay_open = True
                pay_amount = str(request.POST.get('pay_amount', ''))
                pay_method = str(request.POST.get('pay_method', ''))
                card_holder = str(request.POST.get('card_holder', ''))
                card_installments = str(request.POST.get('card_installments', '')).strip()
                transfer_sender = str(request.POST.get('transfer_sender', ''))
                posted_date = str(request.POST.get('pay_date', '')).strip()
                if posted_date:
                    pay_date = posted_date
        except (Party.DoesNotExist, Product.DoesNotExist):
            error = 'Kayıt bulunamadı.'
            if action in {'confirm', 'close', 'delete_payment'} and _wants_json(request):
                return JsonResponse({'ok': False, 'error': error}, status=400)
        job = Job.objects.select_related('party', 'device', 'sale', 'assignee', 'created_by').get(pk=job.pk)
    if tech_mode and job.is_waiting:
        return redirect('portal-service')
    if job.is_waiting:
        today = timezone.localdate()
        seed = job.date if job.date >= today else today
        if request.GET.get('day'):
            chosen = _parse_day(request.GET.get('day'))
            if chosen < today:
                chosen = today
        else:
            chosen = seed
        year, month = parse_year_month(request.GET.get('month'), fallback=chosen)
        view = date(year, month, 1)
        assignee_id, assignee_name = assignment_form_values(job)
        return render(
            request,
            'portal/service_job_pending.html',
            _ctx(
                job=job,
                error=error,
                needs_new_day=job.date < today,
                crew=list(CrewMember.objects.filter(is_active=True)),
                assignee_id=assignee_id,
                assignee_name=assignee_name,
                sold_items=_sold_items(job),
                service_hours=SERVICE_HOUR_LABELS,
                job_time=job.time.strftime('%H:%M') if job.time else '',
                slot_ask=_slot_ask(job),
                **_week_pack(today),
                **_month_browse(view=view, chosen=chosen, today=today),
            ),
        )
    if job.is_open or (job.is_submitted and not tech_mode):
        return render(
            request,
            'portal/service_job_form.html',
            _ctx(**_job_form_context(request, job=job, error=error)),
        )
    sold_groups = sold_unit_groups(job) if job.sale_id else []
    unassigned_units = unassigned_sold_units(job) if job.sale_id else []
    allocations = list(
        job.payment_allocations.select_related('payment', 'payment__created_by').order_by(
            '-payment__date',
            '-id',
        )
    )
    payments = [item.payment for item in allocations]
    pay_has_card = any(item.method == Payment.METHOD_CARD for item in payments)
    pay_has_transfer = any(item.method == Payment.METHOD_TRANSFER for item in payments)
    pay_colspan = 5
    if pay_has_card:
        pay_colspan += 2
    if pay_has_transfer:
        pay_colspan += 1
    lines = list(job.lines.select_related('product'))
    adjust_lines = [
        {
            'qty': str(line.qty),
            'list': str(line.list_unit_price or line.unit_price),
            'vat': str(line.vat_rate),
        }
        for line in lines
    ]
    return render(
        request,
        'portal/service_job_detail.html',
        _ctx(
            job=job,
            lines=lines,
            sold_groups=sold_groups,
            unassigned_units=unassigned_units,
            multi_packs=[group['pack'] for group in sold_groups if group.get('kind') == 'multi'],
            error=error,
            allocations=allocations,
            payments=payments,
            pay_has_card=pay_has_card,
            pay_has_transfer=pay_has_transfer,
            pay_colspan=pay_colspan,
            pay_choices=Payment.METHOD_CHOICES,
            card_installment_choices=Payment.INSTALLMENT_CHOICES,
            pay_open=pay_open,
            pay_amount=pay_amount,
            pay_method=pay_method,
            pay_date=pay_date,
            card_holder=card_holder,
            card_installments=card_installments,
            transfer_sender=transfer_sender,
            today=timezone.localdate().isoformat(),
            pay_remaining=job.remaining,
            pay_grand=job.grand_total,
            pay_paid=job.paid_total,
            pay_copy='Tutar kalanı aşamaz. Genel ve kalan aşağıda durur.',
            show_payment_details=bool(job.is_closed and job.sale_id is None and not tech_mode),
            adjust_lines=adjust_lines,
        ),
    )


@role_required(Customer.ROLE_SERVICE_LEAD)
def reminders(request: HttpRequest) -> HttpResponse:
    today = timezone.localdate()
    horizon = today + timedelta(days=REMINDER_WINDOW_DAYS)
    qs = (
        Device.objects.filter(next_due__isnull=False, next_due__lte=horizon)
        .select_related('party')
        .order_by('next_due', 'name')
    )
    try:
        page = max(1, int(request.GET.get('page', '1')))
    except (TypeError, ValueError):
        page = 1
    paginator = Paginator(qs, JOB_PAGE_SIZE)
    page_obj = paginator.get_page(page)
    return render(
        request,
        'portal/service_reminders.html',
        _ctx(
            devices=page_obj.object_list,
            today=today,
            empty_copy='Yaklaşan bakım yok.' if not paginator.count else '',
            **_page_nav(paginator, page_obj, {}),
        ),
    )
