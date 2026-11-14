import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from accounts.http import uses_field_app

from .models import Notification, PushSubscription
from .notifications import BELL_LIMIT, mark_read, serialize, unread_count

PAGE_SIZE = 30


def _maintenance(user) -> dict | None:
    if not getattr(user, 'can_service_lead', False) or uses_field_app(user):
        return None
    from django.utils import timezone

    from service.services import MAINTENANCE_WINDOW_DAYS, due_maintenance

    today = timezone.localdate()
    qs = due_maintenance(today, MAINTENANCE_WINDOW_DAYS).select_related('party').order_by('next_due', 'name')
    overdue = qs.filter(next_due__lt=today).count()
    total = qs.count()
    return {
        'overdue': overdue,
        'soon': total - overdue,
        'total': total,
        'url': reverse('portal-service-reminders'),
        'items': [
            {
                'party': item.party.display_name if item.party_id else '',
                'device': item.name,
                'interval': item.interval_months,
                'due': item.next_due.strftime('%d.%m.%Y'),
                'overdue': item.next_due < today,
            }
            for item in qs[:5]
        ],
    }


@login_required
@require_GET
def notifications_summary(request: HttpRequest) -> JsonResponse:
    user = request.user
    items = Notification.objects.filter(recipient=user)[:BELL_LIMIT]
    return JsonResponse({
        'ok': True,
        'unread': unread_count(user),
        'items': [serialize(item) for item in items],
        'maintenance': _maintenance(user),
        'url': reverse('portal-notifications'),
        'push_key': settings.VAPID_PUBLIC_KEY if settings.PUSH_ENABLED else '',
    })


@login_required
@require_POST
def notifications_read(request: HttpRequest) -> JsonResponse:
    raw = request.POST.get('ids', '')
    if not raw and request.content_type == 'application/json':
        try:
            raw = json.loads(request.body or b'{}').get('ids', '')
        except ValueError:
            raw = ''
    if raw == 'all' or raw == '':
        changed = mark_read(request.user)
    else:
        parts = raw if isinstance(raw, list) else str(raw).split(',')
        ids = [int(p) for p in parts if str(p).strip().isdigit()]
        changed = mark_read(request.user, ids)
    return JsonResponse({'ok': True, 'changed': changed, 'unread': unread_count(request.user)})


@login_required
@require_GET
def notifications_page(request: HttpRequest) -> HttpResponse:
    user = request.user
    if uses_field_app(user):
        return redirect('portal-field')
    show = str(request.GET.get('show', '')).strip()
    qs = Notification.objects.filter(recipient=user)
    if show == 'unread':
        qs = qs.filter(read_at__isnull=True)
    from service.views import _page_nav

    paginator = Paginator(qs, PAGE_SIZE)
    page = paginator.get_page(request.GET.get('page'))
    return render(
        request,
        'portal/notifications.html',
        {
            'items': page.object_list,
            'show': show,
            'unread': unread_count(user),
            **_page_nav(paginator, page, {'show': show}),
        },
    )


@login_required
@require_http_methods(['POST', 'DELETE'])
def push_subscription(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body or b'{}')
    except ValueError:
        return JsonResponse({'ok': False, 'error': 'Geçersiz istek.'}, status=400)
    endpoint = str(data.get('endpoint', '')).strip()
    if not endpoint.startswith('https://'):
        return JsonResponse({'ok': False, 'error': 'Geçersiz abonelik.'}, status=400)
    if request.method == 'DELETE':
        PushSubscription.objects.filter(user=request.user, endpoint=endpoint).delete()
        return JsonResponse({'ok': True})
    keys = data.get('keys') or {}
    p256dh = str(keys.get('p256dh', '')).strip()
    auth = str(keys.get('auth', '')).strip()
    if not p256dh or not auth:
        return JsonResponse({'ok': False, 'error': 'Geçersiz abonelik.'}, status=400)
    PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={
            'user': request.user,
            'p256dh': p256dh[:200],
            'auth': auth[:100],
            'user_agent': request.headers.get('User-Agent', '')[:300],
        },
    )
    return JsonResponse({'ok': True})
