"""Topbar search: grouped JSON results, role-gated."""

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpRequest, JsonResponse
from django.urls import NoReverseMatch, reverse

from .search import q_search

GROUP_LIMIT = 5
MIN_QUERY = 2


def _tokens(query: str) -> list[str]:
    return [token for token in query.split() if token][:5]


def _all(tokens: list[str], *fields: str) -> Q:
    q = Q()
    for token in tokens:
        q &= q_search(token, *fields)
    return q


def _url(fn) -> str:
    try:
        return fn()
    except NoReverseMatch:
        return ''


def _party_hits(user, tokens):
    from sales.models import Party

    qs = (
        Party.objects.filter(
            _all(tokens, 'first_name', 'last_name', 'company_name', 'phone', 'phone2', 'number', 'tax_no')
        )
        .order_by('-id')[:GROUP_LIMIT]
    )
    sales_ok = user.is_superuser or getattr(user, 'can_sales', False)
    clients = reverse('portal-service-clients')
    items = []
    for party in qs:
        if sales_ok:
            url = _url(party.get_absolute_url)
        else:
            url = f'{clients}?q={party.number}' if party.number else clients
        sub = ' · '.join(part for part in (party.number, party.phone, party.city) if part)
        items.append({'title': party.display_name, 'sub': sub, 'url': url})
    return items


def _sale_hits(tokens):
    from sales.models import Sale

    qs = (
        Sale.objects.filter(
            _all(
                tokens,
                'number',
                'invoice_no',
                'party__first_name',
                'party__last_name',
                'party__company_name',
                'party__number',
                'lines__product__name',
                'lines__product__sku',
            )
        )
        .select_related('party')
        .distinct()
        .order_by('-date', '-id')[:GROUP_LIMIT]
    )
    items = []
    for sale in qs:
        sub = ' · '.join(
            part
            for part in (
                sale.party.display_name if sale.party_id else '',
                sale.date.strftime('%d.%m.%Y') if sale.date else '',
                'Arşiv' if sale.is_archived else '',
            )
            if part
        )
        items.append({'title': sale.number or 'Fiş', 'sub': sub, 'url': _url(sale.get_absolute_url)})
    return items


def _job_hits(user, tokens):
    from service.views import _visible_jobs

    qs = (
        _visible_jobs(user)
        .filter(
            _all(
                tokens,
                'number',
                'party__first_name',
                'party__last_name',
                'party__company_name',
                'party__number',
                'party__phone',
                'party__address',
                'sale__number',
                'sold_units__serial',
                'sold_units__outdoor_serial',
                'sold_packs__outdoor_serial',
            )
        )
        .select_related('party')
        .distinct()
        .order_by('-date', '-id')[:GROUP_LIMIT]
    )
    field_only = not (user.is_superuser or getattr(user, 'can_service_lead', False))
    items = []
    for job in qs:
        url = _url(job.get_field_url if field_only else job.get_absolute_url)
        sub = ' · '.join(
            part
            for part in (
                job.kind_label,
                job.party.display_name if job.party_id else '',
                job.date.strftime('%d.%m.%Y') if job.date else '',
                job.get_status_display(),
            )
            if part
        )
        items.append({'title': job.number, 'sub': sub, 'url': url})
    return items


@login_required
def search_json(request: HttpRequest) -> JsonResponse:
    query = str(request.GET.get('q', '')).strip()[:80]
    tokens = _tokens(query)
    if len(query) < MIN_QUERY or not tokens:
        return JsonResponse({'ok': True, 'q': query, 'groups': []})
    user = request.user
    sales_ok = user.is_superuser or getattr(user, 'can_sales', False)
    lead_ok = user.is_superuser or getattr(user, 'can_service_lead', False)
    field_ok = getattr(user, 'can_service_field', False)
    groups = []
    if sales_ok or lead_ok:
        items = _party_hits(user, tokens)
        if items:
            groups.append({'key': 'parties', 'label': 'Müşteriler', 'items': items})
    if sales_ok:
        items = _sale_hits(tokens)
        if items:
            groups.append({'key': 'sales', 'label': 'Satış fişleri', 'items': items})
    if lead_ok or field_ok:
        items = _job_hits(user, tokens)
        if items:
            groups.append({'key': 'jobs', 'label': 'Servis işleri', 'items': items})
    return JsonResponse({'ok': True, 'q': query, 'groups': groups})
