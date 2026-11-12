import re

from django.contrib.auth.password_validation import validate_password
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from sales.services import format_tr_phone

from .models import Customer

USERNAME_RE = re.compile(r'^[A-Za-z0-9._-]{3,32}$')
RESERVED_USERNAMES = {'new'}


def parse_username(raw) -> str:
    text = str(raw or '').strip().lower()
    if not USERNAME_RE.match(text):
        raise ValueError(
            'Kullanıcı adı 3-32 karakter olmalı; harf, rakam, nokta, tire ve alt çizgi kullanılabilir.'
        )
    if text in RESERVED_USERNAMES:
        raise ValueError('Bu kullanıcı adı kullanılamaz.')
    return text


def parse_email(raw) -> str:
    text = str(raw or '').strip()
    if not text:
        return ''
    try:
        validate_email(text)
    except ValidationError as exc:
        raise ValueError('E-posta geçersiz.') from exc
    return text


def parse_phone(raw) -> str:
    text = str(raw or '').strip()
    if not text:
        return ''
    return format_tr_phone(text, required=False)


def parse_name(raw) -> str:
    return str(raw or '').strip()


def posted_flag(post, name: str) -> bool:
    return str(post.get(name, '')).strip() in {'1', 'on', 'true', 'True'}


def parse_role(raw) -> str:
    text = str(raw or '').strip()
    allowed = {Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD, Customer.ROLE_SERVICE}
    if text not in allowed:
        raise ValueError('Rol seçin.')
    return text


def posted_ids(post, name: str) -> list[int]:
    raw = post.getlist(name) if hasattr(post, 'getlist') else [post.get(name)]
    ids = []
    for item in raw:
        text = str(item or '').strip()
        if text.isdigit():
            ids.append(int(text))
    return ids


def form_values(user: Customer | None = None, post=None) -> dict:
    if post is not None:
        return {
            'username': str(post.get('username', '')).strip().lower(),
            'first_name': parse_name(post.get('first_name')),
            'last_name': parse_name(post.get('last_name')),
            'email': str(post.get('email', '')).strip(),
            'phone': str(post.get('phone', '')).strip(),
            'role': str(post.get('role', '')).strip(),
            'crew_id': str(post.get('crew_id', '')).strip(),
            'stock_category_ids': posted_ids(post, 'stock_category'),
            'is_active': posted_flag(post, 'is_active'),
        }
    if user is not None:
        try:
            crew = user.crew_profile
        except ObjectDoesNotExist:
            crew = None
        return {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user.phone,
            'role': user.role,
            'crew_id': str(crew.pk) if crew else '',
            'stock_category_ids': list(user.stock_categories.values_list('pk', flat=True)),
            'is_active': user.is_active,
        }
    return {
        'username': '',
        'first_name': '',
        'last_name': '',
        'email': '',
        'phone': '',
        'role': '',
        'crew_id': '',
        'stock_category_ids': [],
        'is_active': True,
    }


def apply_profile(user: Customer, post) -> None:
    user.first_name = parse_name(post.get('first_name'))
    user.last_name = parse_name(post.get('last_name'))
    user.email = parse_email(post.get('email'))
    user.phone = parse_phone(post.get('phone'))


def set_user_password(user: Customer, password: str, confirm: str, *, required: bool) -> None:
    password = str(password or '')
    confirm = str(confirm or '')
    if not password:
        if required:
            raise ValueError('Şifre zorunlu.')
        if confirm:
            raise ValueError('Şifreler eşleşmiyor.')
        return
    if password != confirm:
        raise ValueError('Şifreler eşleşmiyor.')
    try:
        validate_password(password, user=user)
    except ValidationError as exc:
        raise ValueError(' '.join(exc.messages)) from exc
    user.set_password(password)


def assignable_crew(*, current=None):
    from crew.models import CrewMember

    qs = CrewMember.objects.filter(is_active=True)
    if current is not None:
        return qs.filter(Q(user__isnull=True) | Q(user=current)).order_by('first_name', 'last_name', 'id')
    return qs.filter(user__isnull=True).order_by('first_name', 'last_name', 'id')


def bind_service_crew(*, user: Customer, crew_id, required: bool = True) -> None:
    from crew.models import CrewMember
    from crew.services import link_member_user

    raw = str(crew_id or '').strip()
    if not raw:
        if required:
            raise ValueError('Servis hesabı bir personel kartına bağlanır.')
        unbind_crew(user=user)
        return
    if not raw.isdigit():
        raise ValueError('Personel kartı bulunamadı.')
    member = CrewMember.objects.filter(pk=int(raw), is_active=True).first()
    if not member:
        raise ValueError('Personel kartı bulunamadı.')
    CrewMember.objects.filter(user=user).exclude(pk=member.pk).update(user=None)
    link_member_user(member=member, user=user)


def unbind_crew(*, user: Customer) -> None:
    from crew.models import CrewMember

    CrewMember.objects.filter(user=user).update(user=None)


def apply_crew(*, user: Customer, role: str, post) -> None:
    if role == Customer.ROLE_SERVICE:
        bind_service_crew(user=user, crew_id=post.get('crew_id'), required=True)
    elif role == Customer.ROLE_SERVICE_LEAD:
        bind_service_crew(user=user, crew_id=post.get('crew_id'), required=False)
    else:
        unbind_crew(user=user)


def sync_stock_categories(*, user: Customer, post) -> None:
    from stock.models import Category

    ids = posted_ids(post, 'stock_category')
    user.stock_categories.set(Category.objects.filter(pk__in=ids))


def apply_access(*, user: Customer, post) -> None:
    role = parse_role(post.get('role'))
    if user.role == Customer.ROLE_SERVICE_LEAD and role != Customer.ROLE_SERVICE_LEAD:
        if user.is_active and not other_active_leads(user):
            raise ValueError('Son servis yetkilisi düşürülemez.')
    apply_crew(user=user, role=role, post=post)
    user.role = role
    user.is_staff = True
    user.save(update_fields=['role', 'is_staff'])
    if role == Customer.ROLE_SERVICE:
        sync_stock_categories(user=user, post=post)
    else:
        user.stock_categories.clear()


@transaction.atomic
def create_portal_user(post) -> Customer:
    username = parse_username(post.get('username'))
    if Customer.objects.filter(username__iexact=username).exists():
        raise ValueError('Bu kullanıcı adı alınmış.')
    role = parse_role(post.get('role'))
    user = Customer(
        username=username,
        role=role,
        is_staff=True,
        is_active=posted_flag(post, 'is_active'),
        is_superuser=False,
    )
    apply_profile(user, post)
    set_user_password(
        user,
        post.get('password', ''),
        post.get('password_confirm', ''),
        required=True,
    )
    user.save()
    apply_access(user=user, post=post)
    return user


@transaction.atomic
def update_portal_user(*, actor: Customer, user: Customer, post, manage_role: bool = True) -> Customer:
    if user.is_superuser and not actor.is_superuser:
        raise ValueError('Yönetici hesabı düzenlenemez.')
    apply_profile(user, post)
    set_user_password(
        user,
        post.get('password', ''),
        post.get('password_confirm', ''),
        required=False,
    )
    user.save()
    if user.is_superuser:
        return user
    if manage_role:
        apply_access(user=user, post=post)
    else:
        apply_crew(user=user, role=user.role, post=post)
    return user


def assert_can_manage(*, actor: Customer, user: Customer) -> None:
    if actor.pk == user.pk:
        raise ValueError('Kendi hesabınızda bu işlem yapılamaz.')
    if user.is_superuser and not actor.is_superuser:
        raise ValueError('Yönetici hesabı düzenlenemez.')


def other_active_leads(user: Customer) -> bool:
    return Customer.objects.filter(
        role=Customer.ROLE_SERVICE_LEAD,
        is_active=True,
    ).exclude(pk=user.pk).exists()


def drop_access(user: Customer) -> None:
    user.tokens.all().delete()
    uid = str(user.pk)
    stale = []
    for session in Session.objects.filter(expire_date__gte=timezone.now()).iterator():
        try:
            data = session.get_decoded()
        except Exception:
            continue
        if str(data.get('_auth_user_id') or '') == uid:
            stale.append(session.pk)
    if stale:
        Session.objects.filter(pk__in=stale).delete()


def set_portal_active(*, actor: Customer, user: Customer, active: bool) -> Customer:
    assert_can_manage(actor=actor, user=user)
    if (
        not active
        and user.role == Customer.ROLE_SERVICE_LEAD
        and not other_active_leads(user)
    ):
        raise ValueError('Son servis yetkilisi pasife alınamaz.')
    user.is_active = active
    user.save(update_fields=['is_active'])
    if not active:
        drop_access(user)
    return user


def delete_portal_user(*, actor: Customer, user: Customer) -> None:
    assert_can_manage(actor=actor, user=user)
    if user.is_superuser:
        raise ValueError('Yönetici hesabı silinemez. Pasife alın.')
    if user.role == Customer.ROLE_SERVICE_LEAD and user.is_active and not other_active_leads(user):
        raise ValueError('Son servis yetkilisi silinemez.')
    drop_access(user)
    try:
        user.delete()
    except ProtectedError as exc:
        raise ValueError(
            'Bu hesabın satış, servis veya stok kaydı var. Silinemez; pasife alın.'
        ) from exc
