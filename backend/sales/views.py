from datetime import date
from decimal import Decimal
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Count, DecimalField, F, IntegerField, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.http import role_required, stock_scope
from accounts.models import Customer
from accounts.portal import _wants_json
from accounts.search import q_search
from accounts.toasts import queue_toast
from accounts.weather import get_weather
from stock.models import Category, Product
from stock.services import StockError

from service.models import Device, Job
from service.services import (
    SERVICE_HOUR_LABELS,
    activate_sale_mount,
    copper_mount_summary,
    month_load_payload,
    party_sold_unit_groups,
    sale_mount_preview_rows,
    sold_unit_groups,
    unassigned_sold_units,
)

from .models import Party, Payment, PaymentAllocation, Sale
from .pdf import sale_pdf_response
from .services import (
    add_party_payment,
    add_payment,
    apply_party_fields,
    compact_party_number,
    create_sale,
    delete_payment,
    delete_sale,
    party_from_post,
    update_invoice,
)


def _ctx(**extra):
    extra.setdefault('weather', get_weather())
    return extra


PARTY_PAGE_SIZE = 6
PARTY_LIST_PAGE_SIZE = 20
SALE_PAGE_SIZE = 20
MONEY_FIELD = DecimalField(max_digits=12, decimal_places=2)
MONEY_ZERO = Value(Decimal('0.00'), output_field=MONEY_FIELD)


def _parse_iso_date(raw):
    text = str(raw or '').strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _sale_categories_for(user):
    # Only klima brands (Euroform / MHI). Merkez Depo is global in product search.
    qs = Category.objects.filter(is_klima=True).order_by('name')
    scope = stock_scope(user)
    if scope is not None:
        qs = qs.filter(pk__in=scope.values_list('pk', flat=True))
    return list(qs)


def _klima_categories_for(user):
    return _sale_categories_for(user)


def _archive_years(today=None):
    today = today or timezone.localdate()
    years = [
        item.year
        for item in Sale.objects.filter(date__year__lt=today.year).dates('date', 'year')
    ]
    years.sort(reverse=True)
    return years


def _sale_querystring(values, page=None):
    data = {}
    for key in ('q', 'invoice', 'kind', 'from', 'to', 'year', 'party'):
        val = str(values.get(key) or '').strip()
        if val:
            data[key] = val
    if page:
        try:
            page_no = int(page)
        except (TypeError, ValueError):
            page_no = 1
        if page_no > 1:
            data['page'] = str(page_no)
    encoded = urlencode(data)
    return f'?{encoded}' if encoded else '?'


def _sale_list_context(request: HttpRequest, *, archive=False):
    today = timezone.localdate()
    current_year = today.year
    archive_years = _archive_years(today)
    query = str(request.GET.get('q', '')).strip()
    invoice = str(request.GET.get('invoice', '')).strip()
    kind = str(request.GET.get('kind', '')).strip()
    date_from = _parse_iso_date(request.GET.get('from'))
    date_to = _parse_iso_date(request.GET.get('to'))
    raw_party = str(request.GET.get('party', '')).strip()
    party_id = int(raw_party) if raw_party.isdigit() else None
    party_filter = Party.objects.filter(pk=party_id).first() if party_id else None
    if party_id and not party_filter:
        party_id = None

    year = None
    raw_year = str(request.GET.get('year', '')).strip()
    if archive:
        if raw_year.isdigit():
            wanted = int(raw_year)
            if wanted in archive_years:
                year = wanted
        elif archive_years:
            year = archive_years[0]
    else:
        year = current_year

    qs = Sale.objects.select_related('party', 'created_by')
    if year:
        qs = qs.filter(date__year=year)
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        if date_from:
            date_from = max(date_from, year_start)
        if date_to:
            date_to = min(date_to, year_end)
        if date_from and date_to and date_from > date_to:
            date_from, date_to = date_to, date_from
    elif archive:
        qs = qs.none()

    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    if invoice in {Sale.INVOICE_YES, Sale.INVOICE_NO}:
        qs = qs.filter(invoice_status=invoice)
    else:
        invoice = ''
    if kind in {Party.KIND_LEGAL, Party.KIND_REAL}:
        qs = qs.filter(party__kind=kind)
    else:
        kind = ''
    if party_id:
        qs = qs.filter(party_id=party_id)

    tokens = [token for token in query.split() if token]
    for token in tokens:
        qs = qs.filter(
            q_search(
                token,
                'number',
                'invoice_no',
                'party__first_name',
                'party__last_name',
                'party__company_name',
                'party__number',
                'party__phone',
                'lines__product__name',
                'lines__product__sku',
                'lines__product__brand',
            )
        )
    if tokens:
        qs = qs.distinct()

    paid_sub = (
        PaymentAllocation.objects.filter(sale_id=OuterRef('pk'))
        .values('sale_id')
        .annotate(total=Sum('amount'))
        .values('total')[:1]
    )
    qs = qs.annotate(
        paid_sum=Coalesce(
            Subquery(paid_sub, output_field=MONEY_FIELD),
            Value(Decimal('0.00'), output_field=MONEY_FIELD),
        )
    ).annotate(remain_sum=F('grand_total') - F('paid_sum'))

    try:
        page = max(1, int(request.GET.get('page', '1')))
    except (TypeError, ValueError):
        page = 1
    paginator = Paginator(qs, SALE_PAGE_SIZE)
    page_obj = paginator.get_page(page)

    filters = {
        'q': query,
        'invoice': invoice,
        'kind': kind,
        'from': date_from.isoformat() if date_from else '',
        'to': date_to.isoformat() if date_to else '',
        'year': str(year) if archive and year else '',
        'party': str(party_id or ''),
    }
    page_links = []
    for num in paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1):
        if num == paginator.ELLIPSIS:
            page_links.append({'label': '…', 'href': '', 'on': False, 'gap': True})
        else:
            page_links.append({
                'label': str(num),
                'href': _sale_querystring(filters, page=num),
                'on': num == page_obj.number,
                'gap': False,
            })

    has_filters = bool(query or invoice or kind or date_from or date_to or party_id)
    if archive and not year:
        empty_copy = 'Geçmiş yıl kaydı yok.'
    elif not page_obj.object_list:
        if has_filters:
            empty_copy = 'Bu süzgeçte fiş yok.'
        elif archive:
            empty_copy = 'Bu yılda satış yok.'
        else:
            empty_copy = 'Henüz satış yok. Yeni satış ile ilk fişi açın.'
    else:
        empty_copy = ''

    year_links = []
    if archive:
        for item in archive_years:
            year_filters = dict(filters)
            year_filters['year'] = str(item)
            year_filters['from'] = ''
            year_filters['to'] = ''
            year_links.append({
                'year': item,
                'on': item == year,
                'href': _sale_querystring(year_filters),
            })

    return {
        'sales': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'page_links': page_links,
        'prev_href': _sale_querystring(filters, page=page_obj.previous_page_number()) if page_obj.has_previous() else '',
        'next_href': _sale_querystring(filters, page=page_obj.next_page_number()) if page_obj.has_next() else '',
        'query': query,
        'invoice': invoice,
        'kind': kind,
        'date_from': filters['from'],
        'date_to': filters['to'],
        'year': year,
        'party_id': party_id or '',
        'party_filter': party_filter,
        'clear_party_href': _sale_querystring({**filters, 'party': ''}),
        'archive': archive,
        'archive_years': archive_years,
        'has_archive': bool(archive_years),
        'current_year': current_year,
        'year_links': year_links,
        'empty_copy': empty_copy,
        'has_filters': has_filters,
    }


def _party_payload(party: Party) -> dict:
    return {
        'ok': True,
        'id': party.pk,
        'number': party.number,
        'name': party.display_name,
        'phone': party.phone,
        'phone2': party.phone2,
        'email': party.email,
        'kind': party.kind,
        'kind_label': party.get_kind_display(),
        'first_name': party.first_name,
        'last_name': party.last_name,
        'national_id': party.national_id,
        'company_name': party.company_name,
        'tax_office': party.tax_office,
        'tax_no': party.tax_no,
        'contact2_name': party.contact2_name,
        'address': party.address,
        'city': party.city,
        'district': party.district,
        'notes': party.notes,
        'url': party.get_absolute_url(),
    }


def _party_querystring(values, page=None):
    data = {}
    for key in ('q', 'kind', 'debt', 'from', 'to'):
        val = str(values.get(key) or '').strip()
        if val:
            data[key] = val
    if page:
        try:
            page_no = int(page)
        except (TypeError, ValueError):
            page_no = 1
        if page_no > 1:
            data['page'] = str(page_no)
    encoded = urlencode(data)
    return f'?{encoded}' if encoded else '?'


def _money_subquery(queryset, group_key, amount_field):
    return (
        queryset.values(group_key)
        .annotate(total=Sum(amount_field))
        .values('total')[:1]
    )


def _count_subquery(queryset, group_key):
    return (
        queryset.values(group_key)
        .annotate(total=Count('id'))
        .values('total')[:1]
    )


def _organic_closed_jobs(*, party=None, party_id=None, date_from=None, date_to=None):
    qs = Job.objects.filter(status=Job.STATUS_CLOSED, sale_id__isnull=True)
    if party is not None:
        qs = qs.filter(party=party)
    elif party_id is not None:
        qs = qs.filter(party_id=party_id)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return qs


def _party_queryset(query: str):
    qs = Party.objects.all()
    tokens = [token for token in query.split() if token]
    for token in tokens:
        qs = qs.filter(
            q_search(
                token,
                'first_name',
                'last_name',
                'company_name',
                'phone',
                'phone2',
                'contact2_name',
                'email',
                'city',
                'district',
                'address',
                'tax_no',
                'national_id',
                'number',
            )
        )
    return qs


def _party_list_context(request: HttpRequest):
    today = timezone.localdate()
    query = str(request.GET.get('q', '')).strip()
    kind = str(request.GET.get('kind', '')).strip()
    debt = str(request.GET.get('debt', '')).strip()
    date_from = _parse_iso_date(request.GET.get('from'))
    date_to = _parse_iso_date(request.GET.get('to'))
    if not date_from and not date_to:
        date_from = date(today.year, 1, 1)
        date_to = today
    elif date_from and date_to and date_from > date_to:
        date_from, date_to = date_to, date_from

    work_qs = Sale.objects.filter(party_id=OuterRef('pk'))
    paid_qs = Payment.objects.filter(party_id=OuterRef('pk'))
    count_qs = Sale.objects.filter(party_id=OuterRef('pk'))
    job_work_qs = _organic_closed_jobs(party_id=OuterRef('pk'))
    if date_from:
        work_qs = work_qs.filter(date__gte=date_from)
        paid_qs = paid_qs.filter(date__gte=date_from)
        count_qs = count_qs.filter(date__gte=date_from)
        job_work_qs = job_work_qs.filter(date__gte=date_from)
    if date_to:
        work_qs = work_qs.filter(date__lte=date_to)
        paid_qs = paid_qs.filter(date__lte=date_to)
        count_qs = count_qs.filter(date__lte=date_to)
        job_work_qs = job_work_qs.filter(date__lte=date_to)

    work_all = Sale.objects.filter(party_id=OuterRef('pk'))
    paid_all = Payment.objects.filter(party_id=OuterRef('pk'))
    job_all = _organic_closed_jobs(party_id=OuterRef('pk'))
    sale_work = Coalesce(
        Subquery(_money_subquery(work_qs, 'party_id', 'grand_total'), output_field=MONEY_FIELD),
        MONEY_ZERO,
    )
    job_work = Coalesce(
        Subquery(_money_subquery(job_work_qs, 'party_id', 'grand_total'), output_field=MONEY_FIELD),
        MONEY_ZERO,
    )
    sale_remain = Coalesce(
        Subquery(_money_subquery(work_all, 'party_id', 'grand_total'), output_field=MONEY_FIELD),
        MONEY_ZERO,
    )
    job_remain = Coalesce(
        Subquery(_money_subquery(job_all, 'party_id', 'grand_total'), output_field=MONEY_FIELD),
        MONEY_ZERO,
    )
    paid_remain = Coalesce(
        Subquery(_money_subquery(paid_all, 'party_id', 'amount'), output_field=MONEY_FIELD),
        MONEY_ZERO,
    )

    qs = _party_queryset(query).annotate(
        work_sum=sale_work + job_work,
        paid_sum=Coalesce(
            Subquery(_money_subquery(paid_qs, 'party_id', 'amount'), output_field=MONEY_FIELD),
            MONEY_ZERO,
        ),
        remain_sum=sale_remain + job_remain - paid_remain,
        sale_count=(
            Coalesce(
                Subquery(_count_subquery(count_qs, 'party_id'), output_field=IntegerField()),
                Value(0),
            )
            + Coalesce(
                Subquery(_count_subquery(job_work_qs, 'party_id'), output_field=IntegerField()),
                Value(0),
            )
        ),
    )
    if kind in {Party.KIND_LEGAL, Party.KIND_REAL}:
        qs = qs.filter(kind=kind)
    else:
        kind = ''
    if debt == 'due':
        qs = qs.filter(remain_sum__gt=Decimal('0.00'))
    elif debt == 'clear':
        qs = qs.filter(remain_sum__lte=Decimal('0.00'))
    else:
        debt = ''

    qs = qs.order_by('-remain_sum', '-work_sum', '-id')

    try:
        page = max(1, int(request.GET.get('page', '1')))
    except (TypeError, ValueError):
        page = 1
    paginator = Paginator(qs, PARTY_LIST_PAGE_SIZE)
    page_obj = paginator.get_page(page)

    filters = {
        'q': query,
        'kind': kind,
        'debt': debt,
        'from': date_from.isoformat() if date_from else '',
        'to': date_to.isoformat() if date_to else '',
    }
    page_links = []
    for num in paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1):
        if num == paginator.ELLIPSIS:
            page_links.append({'label': '…', 'href': '', 'on': False, 'gap': True})
        else:
            page_links.append({
                'label': str(num),
                'href': _party_querystring(filters, page=num),
                'on': num == page_obj.number,
                'gap': False,
            })

    totals = qs.aggregate(
        remain_total=Coalesce(Sum('remain_sum'), MONEY_ZERO),
        work_total=Coalesce(Sum('work_sum'), MONEY_ZERO),
        paid_total=Coalesce(Sum('paid_sum'), MONEY_ZERO),
        due_count=Count('id', filter=Q(remain_sum__gt=Decimal('0.00'))),
    )
    has_filters = bool(query or kind or debt or request.GET.get('from') or request.GET.get('to'))
    if not page_obj.object_list:
        if has_filters:
            empty_copy = 'Bu süzgeçte müşteri yok.'
        else:
            empty_copy = 'Henüz müşteri yok. Yeni müşteri ile ilk kaydı açın.'
    else:
        empty_copy = ''

    return {
        'parties': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'page_links': page_links,
        'prev_href': _party_querystring(filters, page=page_obj.previous_page_number()) if page_obj.has_previous() else '',
        'next_href': _party_querystring(filters, page=page_obj.next_page_number()) if page_obj.has_next() else '',
        'query': query,
        'kind': kind,
        'debt': debt,
        'date_from': filters['from'],
        'date_to': filters['to'],
        'remain_total': totals['remain_total'] or Decimal('0.00'),
        'work_total': totals['work_total'] or Decimal('0.00'),
        'paid_total': totals['paid_total'] or Decimal('0.00'),
        'due_count': totals['due_count'] or 0,
        'empty_copy': empty_copy,
        'has_filters': has_filters,
    }


CUSTOMER_TABS = ('devices', 'sales', 'jobs', 'payments')


def _party_tab(request: HttpRequest) -> str:
    tab = str(request.GET.get('tab', '')).strip()
    if tab in CUSTOMER_TABS:
        return tab
    return 'devices'


def _party_tab_querystring(tab: str, page=None):
    data = {}
    if tab and tab != 'devices':
        data['tab'] = tab
    if page:
        try:
            page_no = int(page)
        except (TypeError, ValueError):
            page_no = 1
        if page_no > 1:
            data['page'] = str(page_no)
    encoded = urlencode(data)
    return f'?{encoded}' if encoded else '?'


def _pay_table_context(payments):
    pay_has_card = any(item.method == Payment.METHOD_CARD for item in payments)
    pay_has_transfer = any(item.method == Payment.METHOD_TRANSFER for item in payments)
    pay_colspan = 5
    if pay_has_card:
        pay_colspan += 2
    if pay_has_transfer:
        pay_colspan += 1
    return {
        'payments': payments,
        'pay_has_card': pay_has_card,
        'pay_has_transfer': pay_has_transfer,
        'pay_colspan': pay_colspan,
    }


def _alloc_paid_subquery(fk_field: str):
    return (
        PaymentAllocation.objects.filter(**{fk_field: OuterRef('pk')})
        .values(fk_field)
        .annotate(total=Sum('amount'))
        .values('total')[:1]
    )


def _party_detail_context(party: Party, request: HttpRequest, extra=None):
    extra = extra or {}
    tab = extra.get('tab') or _party_tab(request)
    sale_paid_sub = _alloc_paid_subquery('sale_id')
    qs = (
        Sale.objects.filter(party=party)
        .select_related('created_by', 'service_job')
        .annotate(
            paid_sum=Coalesce(
                Subquery(sale_paid_sub, output_field=MONEY_FIELD),
                MONEY_ZERO,
            )
        )
        .annotate(remain_sum=F('grand_total') - F('paid_sum'))
    )
    try:
        page = max(1, int(request.GET.get('page', '1')))
    except (TypeError, ValueError):
        page = 1
    paginator = Paginator(qs, SALE_PAGE_SIZE)
    page_obj = paginator.get_page(page)
    page_links = []
    for num in paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1):
        if num == paginator.ELLIPSIS:
            page_links.append({'label': '…', 'href': '', 'on': False, 'gap': True})
        else:
            page_links.append({
                'label': str(num),
                'href': _party_tab_querystring(tab, page=num),
                'on': num == page_obj.number,
                'gap': False,
            })
    work_sum = Sale.objects.filter(party=party).aggregate(s=Sum('grand_total'))['s'] or Decimal('0.00')
    work_sum += (
        _organic_closed_jobs(party=party).aggregate(s=Sum('grand_total'))['s'] or Decimal('0.00')
    )
    paid_sum = (
        Payment.objects.filter(party=party).aggregate(s=Sum('amount'))['s'] or Decimal('0.00')
    )
    remain_sum = work_sum - paid_sum
    sale_count = Sale.objects.filter(party=party).count() + _organic_closed_jobs(party=party).count()
    job_paid_sub = _alloc_paid_subquery('job_id')
    service_jobs = list(
        Job.objects.filter(party=party)
        .exclude(status=Job.STATUS_PENDING)
        .annotate(
            paid_sum=Coalesce(
                Subquery(job_paid_sub, output_field=MONEY_FIELD),
                MONEY_ZERO,
            )
        )
        .annotate(remain_sum=F('grand_total') - F('paid_sum'))
        .order_by('-date', '-id')[:50]
    )
    receipts = list(
        Payment.objects.filter(party=party)
        .select_related('created_by')
        .prefetch_related('allocations__sale', 'allocations__job')
        .order_by('-date', '-id')
    )
    ctx = {
        'party': party,
        'tab': tab,
        'sales': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'page_links': page_links,
        'prev_href': _party_tab_querystring(tab, page=page_obj.previous_page_number()) if page_obj.has_previous() else '',
        'next_href': _party_tab_querystring(tab, page=page_obj.next_page_number()) if page_obj.has_next() else '',
        'work_sum': work_sum,
        'paid_sum': paid_sum,
        'remain_sum': remain_sum,
        'sale_count': sale_count,
        'empty_copy': 'Bu müşteride satış yok.' if not qs.exists() else '',
        'service_jobs': service_jobs,
        'receipts': receipts,
        'edit_party_payload': _party_payload(party),
        'devices': Device.objects.filter(party=party),
        'sold_groups': party_sold_unit_groups(party),
        'today': timezone.localdate(),
        'pay_choices': Payment.METHOD_CHOICES,
        'card_installment_choices': Payment.INSTALLMENT_CHOICES,
        'pay_remaining': remain_sum,
        'pay_grand': work_sum,
        'pay_paid': paid_sum,
        'pay_copy': 'Tutar en eski açık bakiyeden başlayarak dağılır. Kalanı aşamaz.',
        'pay_title': 'Tahsilat ekle',
        'pay_open': False,
        'pay_amount': '',
        'pay_method': '',
        'pay_date': timezone.localdate().isoformat(),
        'card_holder': '',
        'card_installments': '',
        'transfer_sender': '',
        **_pay_table_context(receipts),
    }
    ctx.update(extra)
    return ctx


def party_search_json(request: HttpRequest) -> JsonResponse:
    query = str(request.GET.get('q', '')).strip()
    try:
        page = max(1, int(request.GET.get('page', '1')))
    except (TypeError, ValueError):
        page = 1
    paginator = Paginator(_party_queryset(query), PARTY_PAGE_SIZE)
    page_obj = paginator.get_page(page)
    return JsonResponse(
        {
            'ok': True,
            'results': [_party_payload(item) for item in page_obj.object_list],
            'page': page_obj.number,
            'pages': paginator.num_pages,
            'count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_prev': page_obj.has_previous(),
        }
    )


@role_required(Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD)
def sale_list(request: HttpRequest) -> HttpResponse:
    return render(request, 'portal/sales.html', _ctx(**_sale_list_context(request)))


@role_required(Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD)
def sale_archive(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'portal/sales_archive.html',
        _ctx(**_sale_list_context(request, archive=True)),
    )


@role_required(Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD)
@require_http_methods(['GET', 'POST'])
def sale_new(request: HttpRequest) -> HttpResponse:
    error = ''
    if request.method == 'POST':
        try:
            sale = create_sale(user=request.user, post=request.POST)
            queue_toast(request, 'Satış fişi oluşturuldu.')
            if _wants_json(request):
                return JsonResponse(
                    {
                        'ok': True,
                        'id': sale.pk,
                        'url': sale.get_absolute_url(),
                        'toast': 'Satış fişi oluşturuldu.',
                    }
                )
            return redirect(sale.get_absolute_url())
        except (ValueError, StockError, Product.DoesNotExist, Party.DoesNotExist) as exc:
            error = str(exc)
            if _wants_json(request):
                return JsonResponse({'ok': False, 'error': error}, status=400)
    today = timezone.localdate()
    return render(
        request,
        'portal/sales_form.html',
        _ctx(
            error=error,
            today=today.isoformat(),
            vat_choices=Sale.VAT_CHOICES,
            invoice_choices=Sale.INVOICE_CHOICES,
            pay_choices=Payment.METHOD_CHOICES,
            card_installment_choices=Payment.INSTALLMENT_CHOICES,
            service_load=month_load_payload(today.year, today.month),
            service_hours=SERVICE_HOUR_LABELS,
            sale_categories=_sale_categories_for(request.user),
            klima_categories=_klima_categories_for(request.user),
        ),
    )


@role_required(Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD)
def sale_detail_redirect(request: HttpRequest, pk: int) -> HttpResponse:
    sale = get_object_or_404(Sale, pk=pk)
    return redirect(sale.get_absolute_url(), permanent=True)


@role_required(Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD)
@require_http_methods(['GET', 'POST'])
def sale_archive_detail(request: HttpRequest, number: str) -> HttpResponse:
    return _sale_detail(request, number, archive_route=True)


@role_required(Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD)
@require_http_methods(['GET', 'POST'])
def sale_detail(request: HttpRequest, number: str) -> HttpResponse:
    return _sale_detail(request, number, archive_route=False)


def _sale_detail(request: HttpRequest, number: str, *, archive_route: bool) -> HttpResponse:
    sale = get_object_or_404(
        Sale.objects.select_related('party', 'created_by', 'updated_by', 'service_job'),
        number=number,
    )
    if sale.is_archived != archive_route:
        return redirect(sale.get_absolute_url(), permanent=True)
    if request.method == 'GET' and request.GET.get('format') == 'pdf':
        return sale_pdf_response(sale, download=request.GET.get('download') == '1')
    error = ''
    pay_open = False
    pay_amount = ''
    pay_method = ''
    pay_date = timezone.localdate().isoformat()
    card_holder = ''
    card_installments = ''
    transfer_sender = ''
    invoice_open = False
    invoice_status = sale.invoice_status
    invoice_no = sale.invoice_no
    if request.method == 'POST':
        action = str(request.POST.get('action', '')).strip()
        try:
            if action == 'payment':
                add_payment(sale=sale, user=request.user, post=request.POST)
                queue_toast(request, 'Ödeme kaydedildi.')
            elif action == 'delete_payment':
                delete_payment(user=request.user, post=request.POST, sale=sale)
                queue_toast(request, 'Tahsilat silindi.')
                if _wants_json(request):
                    return JsonResponse(
                        {
                            'ok': True,
                            'url': sale.get_absolute_url(),
                            'toast': 'Tahsilat silindi.',
                        }
                    )
            elif action == 'invoice':
                update_invoice(sale=sale, user=request.user, post=request.POST)
                queue_toast(request, 'Fatura bilgisi güncellendi.')
            elif action == 'delete':
                list_url = sale.get_list_url()
                delete_sale(sale=sale, user=request.user)
                queue_toast(request, 'Satış fişi silindi.')
                if _wants_json(request):
                    return JsonResponse({'ok': True, 'url': list_url, 'toast': 'Satış fişi silindi.'})
                return redirect(list_url)
            else:
                error = 'Bilinmeyen işlem.'
            sale.refresh_from_db()
            invoice_status = sale.invoice_status
            invoice_no = sale.invoice_no
        except ValueError as exc:
            error = str(exc)
            if action in {'delete', 'delete_payment'} and _wants_json(request):
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
            elif action == 'invoice':
                invoice_open = True
                invoice_status = str(request.POST.get('invoice_status', sale.invoice_status)).strip()
                invoice_no = str(request.POST.get('invoice_no', sale.invoice_no)).strip()
    allocations = list(
        sale.payment_allocations.select_related('payment', 'payment__created_by').order_by(
            '-payment__date',
            '-id',
        )
    )
    payments = [item.payment for item in allocations]
    try:
        job = sale.service_job
    except Job.DoesNotExist:
        job = None
    sold_groups = sold_unit_groups(job) if job else []
    unassigned_units = unassigned_sold_units(job) if job else []
    multi_packs = [group['pack'] for group in sold_groups if group.get('kind') == 'multi']
    return render(
        request,
        'portal/sales_detail.html',
        _ctx(
            sale=sale,
            error=error,
            lines=sale.lines.select_related('product'),
            sold_groups=sold_groups,
            unassigned_units=unassigned_units,
            multi_packs=multi_packs,
            copper_summary=copper_mount_summary(job) if job else None,
            allocations=allocations,
            **_pay_table_context(payments),
            invoice_choices=Sale.INVOICE_CHOICES,
            pay_choices=Payment.METHOD_CHOICES,
            today=timezone.localdate().isoformat(),
            pay_open=pay_open,
            pay_amount=pay_amount,
            pay_method=pay_method,
            pay_date=pay_date,
            card_holder=card_holder,
            card_installments=card_installments,
            transfer_sender=transfer_sender,
            card_installment_choices=Payment.INSTALLMENT_CHOICES,
            invoice_open=invoice_open,
            invoice_status=invoice_status,
            invoice_no=invoice_no,
        ),
    )


@role_required(Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD)
@require_http_methods(['GET', 'POST'])
def customer_list(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET' and _wants_json(request):
        return party_search_json(request)
    error = ''
    if request.method == 'POST':
        try:
            party = party_from_post(request.POST, request.user)
            text = queue_toast(request, 'Müşteri kaydı oluşturuldu.')
            if _wants_json(request):
                payload = _party_payload(party)
                payload['toast'] = text
                return JsonResponse(payload)
            return redirect('portal-sales-customers')
        except ValueError as exc:
            if _wants_json(request):
                return JsonResponse({'ok': False, 'error': str(exc)}, status=400)
            error = str(exc)
    return render(
        request,
        'portal/sales_customers.html',
        _ctx(**_party_list_context(request), error=error),
    )


@role_required(Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD)
def customer_detail_redirect(request: HttpRequest, pk: int) -> HttpResponse:
    party = get_object_or_404(Party, pk=pk)
    return redirect(party.get_absolute_url(), permanent=True)


@role_required(Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD)
@require_http_methods(['GET', 'POST'])
def customer_edit(request: HttpRequest, number: str) -> HttpResponse:
    party = get_object_or_404(Party, number=compact_party_number(number))
    if request.method == 'GET' and _wants_json(request):
        return JsonResponse(_party_payload(party))
    error = ''
    party_modal_open = False
    pay_open = False
    pay_amount = ''
    pay_method = ''
    pay_date = timezone.localdate().isoformat()
    card_holder = ''
    card_installments = ''
    transfer_sender = ''
    tab = _party_tab(request)
    if request.method == 'POST':
        action = str(request.POST.get('action', '')).strip()
        try:
            if action == 'payment':
                add_party_payment(party=party, user=request.user, post=request.POST)
                queue_toast(request, 'Ödeme kaydedildi.')
                tab = 'payments'
                if _wants_json(request):
                    return JsonResponse(
                        {
                            'ok': True,
                            'url': f"{party.get_absolute_url()}?tab=payments",
                            'toast': 'Ödeme kaydedildi.',
                        }
                    )
                return redirect(f"{party.get_absolute_url()}?tab=payments")
            if action == 'delete_payment':
                delete_payment(user=request.user, post=request.POST, party=party)
                queue_toast(request, 'Tahsilat silindi.')
                tab = 'payments'
                if _wants_json(request):
                    return JsonResponse(
                        {
                            'ok': True,
                            'url': f"{party.get_absolute_url()}?tab=payments",
                            'toast': 'Tahsilat silindi.',
                        }
                    )
                return redirect(f"{party.get_absolute_url()}?tab=payments")
            apply_party_fields(party, request.POST)
            text = queue_toast(request, 'Müşteri kaydı güncellendi.')
            if _wants_json(request):
                payload = _party_payload(party)
                payload['toast'] = text
                return JsonResponse(payload)
            return redirect(party.get_absolute_url())
        except ValueError as exc:
            if action in {'delete', 'delete_payment'} and _wants_json(request):
                return JsonResponse({'ok': False, 'error': str(exc)}, status=400)
            if _wants_json(request) and action not in {'payment', 'delete_payment'}:
                return JsonResponse({'ok': False, 'error': str(exc)}, status=400)
            error = str(exc)
            if action == 'payment':
                tab = 'payments'
                pay_open = True
                pay_amount = str(request.POST.get('pay_amount', ''))
                pay_method = str(request.POST.get('pay_method', ''))
                card_holder = str(request.POST.get('card_holder', ''))
                card_installments = str(request.POST.get('card_installments', '')).strip()
                transfer_sender = str(request.POST.get('transfer_sender', ''))
                posted_date = str(request.POST.get('pay_date', '')).strip()
                if posted_date:
                    pay_date = posted_date
            elif action == 'delete_payment':
                tab = 'payments'
            else:
                party_modal_open = True
    return render(
        request,
        'portal/sales_customer_detail.html',
        _ctx(
            **_party_detail_context(
                party,
                request,
                extra={
                    'tab': tab,
                    'error': error,
                    'party_modal_open': party_modal_open,
                    'pay_open': pay_open,
                    'pay_amount': pay_amount,
                    'pay_method': pay_method,
                    'pay_date': pay_date,
                    'card_holder': card_holder,
                    'card_installments': card_installments,
                    'transfer_sender': transfer_sender,
                },
            ),
        ),
    )


def _missing_mount_days():
    linked = Job.objects.filter(sale_id__isnull=False).values_list('sale_id', flat=True)
    sales = (
        Sale.objects.filter(work_type=Sale.WORK_DEVICE)
        .exclude(pk__in=linked)
        .select_related('party')
        .prefetch_related('lines__product', 'lines__product__outdoor', 'lines__product__category')
        .order_by('date', 'id')
    )
    days = []
    current = None
    bucket = None
    for sale in sales:
        rows = sale_mount_preview_rows(sale)
        if not rows:
            continue
        if current != sale.date:
            current = sale.date
            bucket = {'date': sale.date, 'sales': []}
            days.append(bucket)
        bucket['sales'].append({'sale': sale, 'rows': rows})
    return days


@role_required(Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD)
@require_http_methods(['GET', 'POST'])
def mount_activation(request: HttpRequest) -> HttpResponse:
    """Temporary backfill panel — remove after historical mounts are activated."""
    error = ''
    if request.method == 'POST':
        sale_id = str(request.POST.get('sale_id', '')).strip()
        try:
            if not sale_id.isdigit():
                raise ValueError('Satış seçin.')
            sale = Sale.objects.select_related('party').get(pk=int(sale_id), work_type=Sale.WORK_DEVICE)
            job = activate_sale_mount(sale=sale, user=request.user, post=request.POST)
            push_toast(request, f'{sale.number} montajı aktif · {job.device.name if job.device_id else "cihaz"}')
            return redirect('portal-sales-mount-activation')
        except (ValueError, Sale.DoesNotExist) as exc:
            error = str(exc)
    return render(
        request,
        'portal/sales_mount_activation.html',
        _ctx(
            days=_missing_mount_days(),
            care_intervals=[(3, '3 ay'), (6, '6 ay'), (9, '9 ay'), (12, '12 ay')],
            error=error,
        ),
    )
