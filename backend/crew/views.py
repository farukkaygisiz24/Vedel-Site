from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.http import role_required
from accounts.models import Customer
from accounts.search import q_search
from accounts.toasts import queue_toast
from accounts.weather import get_weather

from .models import CrewDocument, CrewMember
from .services import (
    DOC_WINDOW_DAYS,
    add_document,
    compact_crew_number,
    create_member,
    delete_document,
    download_document,
    member_form_values,
    posted_document_rows,
    reminder_bounds,
    save_member_access,
    update_member,
)

CREW_PAGE_SIZE = 20


def _ctx(**extra):
    extra.setdefault('weather', get_weather())
    return extra


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


def _member_q(query: str):
    q = Q()
    for token in query.split():
        q &= q_search(
            token,
            'number',
            'first_name',
            'last_name',
            'phone',
            'phone2',
            'title',
            'national_id',
            'address',
            'city',
            'district',
        )
    return q


@role_required(Customer.ROLE_SERVICE_LEAD)
def crew_list(request: HttpRequest) -> HttpResponse:
    query = str(request.GET.get('q', '')).strip()
    qs = CrewMember.objects.all()
    if query:
        qs = qs.filter(_member_q(query))
    try:
        page = max(1, int(request.GET.get('page', '1')))
    except (TypeError, ValueError):
        page = 1
    paginator = Paginator(qs, CREW_PAGE_SIZE)
    page_obj = paginator.get_page(page)
    today, horizon = reminder_bounds()
    docs = CrewDocument.objects.select_related('member').order_by('expires_on', 'title')
    expired = list(docs.filter(expires_on__lt=today))
    soon = list(docs.filter(expires_on__gte=today, expires_on__lte=horizon))
    if not page_obj.object_list:
        empty_copy = 'Bu süzgeçte personel yok.' if query else 'Henüz personel yok. Yeni kart ile ekleyin.'
    else:
        empty_copy = ''
    return render(
        request,
        'portal/crew.html',
        _ctx(
            members=page_obj.object_list,
            query=query,
            member_count=CrewMember.objects.count(),
            expired=expired,
            soon=soon,
            expired_count=len(expired),
            soon_count=len(soon),
            today=today,
            window_days=DOC_WINDOW_DAYS,
            empty_copy=empty_copy,
            **_page_nav(paginator, page_obj, {'q': query}),
        ),
    )


@role_required(Customer.ROLE_SERVICE_LEAD)
@require_http_methods(['GET', 'POST'])
def crew_new(request: HttpRequest) -> HttpResponse:
    error = ''
    today = timezone.localdate()
    form = member_form_values(post=request.POST if request.method == 'POST' else None)
    doc_rows = posted_document_rows(request.POST, today=today) if request.method == 'POST' else [
        {'title': '', 'expires_on': today.isoformat()},
        {'title': '', 'expires_on': today.isoformat()},
    ]
    if request.method == 'POST':
        try:
            member = create_member(user=request.user, post=request.POST, files=request.FILES)
            queue_toast(request, 'Personel kartı açıldı.')
            return redirect(member.get_absolute_url())
        except ValueError as exc:
            error = str(exc)
    return render(
        request,
        'portal/crew_new.html',
        _ctx(
            error=error,
            form=form,
            doc_rows=doc_rows,
            today_iso=today.isoformat(),
            empty_doc_row={'title': '', 'expires_on': today.isoformat()},
        ),
    )


@role_required(Customer.ROLE_SERVICE_LEAD)
@require_http_methods(['GET', 'POST'])
def crew_item(request: HttpRequest, number: str) -> HttpResponse:
    member = get_object_or_404(CrewMember, number=compact_crew_number(number))
    if request.method == 'GET' and str(request.GET.get('file', '')).strip():
        return download_document(member=member, raw_id=str(request.GET.get('file', '')).strip())
    error = ''
    edit_open = False
    form = member_form_values(member)
    if request.method == 'POST':
        action = str(request.POST.get('action', '')).strip()
        try:
            if action == 'add_doc':
                add_document(member=member, user=request.user, post=request.POST, files=request.FILES)
                queue_toast(request, 'Evrak eklendi.')
            elif action == 'delete_doc':
                delete_document(member=member, post=request.POST)
                queue_toast(request, 'Evrak silindi.')
            elif action == 'save_access':
                save_member_access(member=member, post=request.POST)
                queue_toast(request, 'Yazıcı kaydedildi.')
            else:
                update_member(member=member, user=request.user, post=request.POST)
                queue_toast(request, 'Personel güncellendi.')
            return redirect(member.get_absolute_url())
        except ValueError as exc:
            error = str(exc)
            if action not in {'add_doc', 'delete_doc', 'save_access'}:
                edit_open = True
                form = member_form_values(post=request.POST)
        member = CrewMember.objects.get(pk=member.pk)
    today, horizon = reminder_bounds()
    documents = list(member.documents.all())
    expired_count = sum(1 for item in documents if item.expires_on < today)
    soon_count = sum(1 for item in documents if today <= item.expires_on <= horizon)
    return render(
        request,
        'portal/crew_item.html',
        _ctx(
            member=member,
            form=form,
            documents=documents,
            error=error,
            edit_open=edit_open,
            today=today,
            horizon=horizon,
            today_iso=today.isoformat(),
            expired_count=expired_count,
            soon_count=soon_count,
            window_days=DOC_WINDOW_DAYS,
        ),
    )
