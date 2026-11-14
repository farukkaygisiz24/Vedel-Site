"""Persistent notification center (topbar bell, /notifications/, field bell).

`notify()` is the single entry point: it stores one row per recipient, pushes a
live `notification` event to each recipient's socket and (optionally) a web push.
The actor never notifies themselves.
"""

from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from . import push
from .models import Customer, Notification
from .realtime import send_to_users

KEEP_DAYS = 90
BELL_LIMIT = 10


def unread_count(user) -> int:
    return Notification.objects.filter(recipient=user, read_at__isnull=True).count()


def serialize(item: Notification) -> dict:
    return {
        'id': item.pk,
        'kind': item.kind,
        'title': item.title,
        'body': item.body,
        'url': item.url,
        'read': item.read_at is not None,
        'at': timezone.localtime(item.created_at).isoformat(),
    }


def notify(recipients, *, kind: str, title: str, body: str = '', url: str = '', actor=None,
           dedupe_key: str = '', send_push: bool = True) -> list[Notification]:
    actor_id = getattr(actor, 'pk', actor)
    ids = []
    for item in recipients:
        uid = getattr(item, 'pk', item)
        if uid and uid != actor_id and uid not in ids:
            ids.append(uid)
    if dedupe_key:
        seen = set(
            Notification.objects.filter(recipient_id__in=ids, dedupe_key=dedupe_key)
            .values_list('recipient_id', flat=True)
        )
        ids = [uid for uid in ids if uid not in seen]
    if not ids:
        return []
    rows = Notification.objects.bulk_create([
        Notification(
            recipient_id=uid,
            kind=kind,
            title=title[:160],
            body=body[:300],
            url=url[:300],
            actor_id=actor_id,
            dedupe_key=dedupe_key,
        )
        for uid in ids
    ])
    for row in rows:
        send_to_users(
            [row.recipient_id],
            'notification',
            actor_id=actor_id,
            text=title,
            obj_id=row.pk,
            extra={'notification': serialize(row), 'unread': None},
        )
    if send_push:
        push.send(ids, title=title, body=body, url=url, tag=dedupe_key or kind)
    return rows


def mark_read(user, ids=None) -> int:
    qs = Notification.objects.filter(recipient=user, read_at__isnull=True)
    if ids is not None:
        qs = qs.filter(pk__in=ids)
    return qs.update(read_at=timezone.now())


def prune(now=None) -> int:
    cutoff = (now or timezone.now()) - timedelta(days=KEEP_DAYS)
    deleted, _ = Notification.objects.filter(created_at__lt=cutoff).delete()
    return deleted


def users_with(flag: str):
    """Active portal users that have a Customer role flag (e.g. 'can_sales')."""
    qs = Customer.objects.filter(is_active=True).filter(Q(is_staff=True) | Q(is_superuser=True))
    return [user for user in qs if getattr(user, flag, False)]
