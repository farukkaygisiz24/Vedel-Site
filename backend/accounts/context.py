from django.contrib.messages import get_messages

from accounts.http import crew_member_for, is_field_user, stock_scope, uses_field_app


def portal_toasts(request):
    return {'portal_toasts': [str(item) for item in get_messages(request)]}


def tr_locations(request):
    from sales.tr_locations import DEFAULT_CITY, TR_CITIES

    return {'tr_cities': TR_CITIES, 'tr_default_city': DEFAULT_CITY}


def field_nav(request):
    user = getattr(request, 'user', None)
    member = crew_member_for(user)
    field = is_field_user(user)
    app = uses_field_app(user)
    staff = bool(user and getattr(user, 'is_authenticated', False) and getattr(user, 'is_staff', False))
    return {
        'crew_member': member,
        'is_field_user': field,
        'uses_field_app': app,
        'show_office_nav': staff and not app,
        'show_field_nav': bool(staff and not app and getattr(user, 'can_service_lead', False)),
        'field_home': app,
    }


def portal_caps(request):
    user = getattr(request, 'user', None)
    auth = bool(user and getattr(user, 'is_authenticated', False))

    def flag(name):
        return bool(auth and getattr(user, name, False))

    return {
        'can_sales': flag('can_sales'),
        'can_service_lead': flag('can_service_lead'),
        'can_service_field': flag('can_service_field'),
        'can_service': flag('can_service'),
        'can_stock': flag('can_stock'),
        'can_stock_manage': flag('can_stock_manage'),
        'can_users': flag('can_users'),
        'can_crew': flag('can_crew'),
    }


def stock_nav(request):
    user = getattr(request, 'user', None)
    if not user or not getattr(user, 'is_authenticated', False) or not getattr(user, 'can_stock', False):
        return {'stock_categories': []}
    from stock.models import Category
    from stock.services import (
        DEFAULT_CATEGORY_SLUG,
        COPPER_CATEGORY_SLUG,
        MOUNT_CATEGORY_SLUG,
        copper_category,
        default_category,
        mount_category,
    )

    if getattr(user, 'can_stock_manage', False):
        default_category(user)
        mount_category(user)
        copper_category(user)
    scope = stock_scope(user)
    cats = list(Category.objects.all() if scope is None else scope)
    order = {DEFAULT_CATEGORY_SLUG: 0, MOUNT_CATEGORY_SLUG: 1, COPPER_CATEGORY_SLUG: 2}
    cats.sort(key=lambda item: (order.get(item.slug, 3), item.name))
    return {'stock_categories': cats}
