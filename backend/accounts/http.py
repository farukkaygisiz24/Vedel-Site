from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse


def crew_member_for(user):
    if not user or not getattr(user, 'is_authenticated', False):
        return None
    try:
        return user.crew_profile
    except (ObjectDoesNotExist, AttributeError):
        return None


def is_field_user(user) -> bool:
    member = crew_member_for(user)
    return bool(member and member.is_active)


def uses_field_app(user) -> bool:
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    if getattr(user, 'can_service_lead', False) or getattr(user, 'is_superuser', False):
        return False
    return bool(getattr(user, 'can_service_field', False) or is_field_user(user))


def home_url_name(user) -> str:
    if uses_field_app(user):
        return 'portal-field'
    if getattr(user, 'is_staff', False):
        return 'portal-dashboard'
    if is_field_user(user):
        return 'portal-field'
    return 'portal-dashboard'


def home_path(user) -> str:
    return reverse(home_url_name(user))


def staff_required(view):
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        user = request.user
        if uses_field_app(user) or not user.is_staff:
            return redirect(home_url_name(user))
        return view(request, *args, **kwargs)

    return wrapped


def role_required(*roles):
    allowed = frozenset(roles)

    def decorator(view):
        @staff_required
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            user = request.user
            if user.is_superuser or getattr(user, 'role', '') in allowed:
                return view(request, *args, **kwargs)
            return redirect(home_url_name(user))

        return wrapped

    return decorator


def field_required(view):
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        user = request.user
        if uses_field_app(user) or getattr(user, 'can_service_lead', False) or getattr(user, 'is_superuser', False):
            return view(request, *args, **kwargs)
        return redirect(home_url_name(user))

    return wrapped


def stock_scope(user):
    from stock.models import Category

    if not user or not getattr(user, 'is_authenticated', False):
        return Category.objects.none()
    if getattr(user, 'can_service_field', False) and not getattr(user, 'can_service_lead', False):
        return user.stock_categories.all()
    if getattr(user, 'can_stock', False):
        return None
    return Category.objects.none()


def can_access_category(user, category) -> bool:
    if not category:
        return getattr(user, 'can_stock_manage', False)
    scope = stock_scope(user)
    if scope is None:
        return True
    return scope.filter(pk=category.pk).exists()


class DebugTrustHostOriginMiddleware:
    """Allow phone/LAN/tunnel hosts to POST (login) while DEBUG is on."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.conf import settings

        if settings.DEBUG:
            forwarded = request.META.get('HTTP_X_FORWARDED_PROTO', '')
            scheme = (
                forwarded.split(',')[0].strip()
                if forwarded
                else ('https' if request.is_secure() else 'http')
            )
            origin = f'{scheme}://{request.get_host()}'
            trusted = settings.CSRF_TRUSTED_ORIGINS
            if origin not in trusted:
                trusted.append(origin)
        return self.get_response(request)


class DisableBrowserCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-store, max-age=0'
        response['Pragma'] = 'no-cache'
        return response
