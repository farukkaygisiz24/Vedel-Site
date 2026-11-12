from urllib.parse import urlencode

from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from accounts.http import role_required
from accounts.toasts import queue_toast
from accounts.weather import get_weather
from stock.models import Category
from stock.services import DEFAULT_CATEGORY_SLUG, MOUNT_CATEGORY_SLUG

from .models import Customer
from .user_services import (
    assignable_crew,
    create_portal_user,
    delete_portal_user,
    form_values,
    set_portal_active,
    update_portal_user,
)

USER_PAGE_SIZE = 20


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


def _role_form_extras(*, account=None):
    cats = list(Category.objects.all())
    order = {DEFAULT_CATEGORY_SLUG: 0, MOUNT_CATEGORY_SLUG: 1}
    cats.sort(key=lambda item: (order.get(item.slug, 2), item.name))
    return {
        'crew_choices': list(assignable_crew(current=account)),
        'stock_category_choices': cats,
        'role_choices': Customer.ROLE_CHOICES,
    }


def _user_q(query: str):
    q = Q()
    for token in query.split():
        q &= (
            Q(username__icontains=token)
            | Q(first_name__icontains=token)
            | Q(last_name__icontains=token)
            | Q(email__icontains=token)
            | Q(phone__icontains=token)
        )
    return q


@role_required(Customer.ROLE_SERVICE_LEAD)
def user_list(request: HttpRequest) -> HttpResponse:
    query = str(request.GET.get('q', '')).strip()
    qs = Customer.objects.all().order_by('username')
    if query:
        qs = qs.filter(_user_q(query))
    try:
        page = max(1, int(request.GET.get('page', '1')))
    except (TypeError, ValueError):
        page = 1
    paginator = Paginator(qs, USER_PAGE_SIZE)
    page_obj = paginator.get_page(page)
    all_users = Customer.objects.all()
    if not page_obj.object_list:
        empty_copy = 'Bu süzgeçte kullanıcı yok.' if query else 'Henüz kullanıcı yok. Yeni kullanıcı ile ekleyin.'
    else:
        empty_copy = ''
    return render(
        request,
        'portal/users.html',
        _ctx(
            users=page_obj.object_list,
            query=query,
            user_count=all_users.count(),
            staff_count=all_users.filter(role=Customer.ROLE_SERVICE_LEAD).count(),
            active_count=all_users.filter(is_active=True).count(),
            inactive_count=all_users.filter(is_active=False).count(),
            empty_copy=empty_copy,
            **_page_nav(paginator, page_obj, {'q': query}),
        ),
    )


@role_required(Customer.ROLE_SERVICE_LEAD)
@require_http_methods(['GET', 'POST'])
def user_new(request: HttpRequest) -> HttpResponse:
    error = ''
    form = form_values(post=request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        try:
            account = create_portal_user(request.POST)
            queue_toast(request, 'Kullanıcı hesabı açıldı.')
            return redirect(account.get_absolute_url())
        except ValueError as exc:
            error = str(exc)
    return render(
        request,
        'portal/users_new.html',
        _ctx(
            error=error,
            form=form,
            creating=True,
            lock_role=False,
            **_role_form_extras(),
        ),
    )


@role_required(Customer.ROLE_SERVICE_LEAD)
@require_http_methods(['GET', 'POST'])
def user_item(request: HttpRequest, username: str) -> HttpResponse:
    account = get_object_or_404(
        Customer.objects.select_related('crew_profile').prefetch_related('stock_categories'),
        username__iexact=username,
    )
    error = ''
    edit_open = False
    form = form_values(account)
    lock_flags = request.user.pk == account.pk
    can_edit = (not account.is_superuser) or request.user.is_superuser
    can_manage = can_edit and not lock_flags
    if request.method == 'POST':
        action = str(request.POST.get('action', 'save')).strip() or 'save'
        try:
            if action == 'save':
                if not can_edit:
                    raise ValueError('Yönetici hesabı düzenlenemez.')
                account = update_portal_user(
                    actor=request.user,
                    user=account,
                    post=request.POST,
                    manage_role=can_manage,
                )
                if str(request.POST.get('password', '')).strip() and request.user.pk == account.pk:
                    login(request, account)
                queue_toast(request, 'Kullanıcı güncellendi.')
                return redirect(account.get_absolute_url())
            if not can_manage:
                raise ValueError('Kendi hesabınızda bu işlem yapılamaz.')
            if action == 'deactivate':
                set_portal_active(actor=request.user, user=account, active=False)
                queue_toast(request, 'Hesap pasife alındı. Panele giriş kapandı.')
            elif action == 'activate':
                set_portal_active(actor=request.user, user=account, active=True)
                queue_toast(request, 'Hesap yeniden açıldı.')
            elif action == 'delete':
                delete_portal_user(actor=request.user, user=account)
                queue_toast(request, 'Hesap silindi.')
                return redirect(reverse('portal-users'))
            else:
                raise ValueError('İşlem geçersiz.')
            return redirect(account.get_absolute_url())
        except ValueError as exc:
            error = str(exc)
            edit_open = action == 'save'
            if edit_open:
                form = form_values(post=request.POST)
        account = Customer.objects.filter(pk=account.pk).first() or account
        if not edit_open:
            form = form_values(account)
    return render(
        request,
        'portal/users_item.html',
        _ctx(
            account=account,
            form=form,
            error=error,
            edit_open=edit_open,
            creating=False,
            lock_flags=lock_flags,
            can_edit=can_edit,
            can_manage=can_manage,
            lock_role=lock_flags or account.is_superuser,
            password_open=bool(error) and edit_open and ('şifre' in error.lower() or 'parola' in error.lower()),
            **_role_form_extras(account=account),
        ),
    )
