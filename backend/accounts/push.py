"""Web push to installed portal apps (field phones, office browsers).

Sends run in a background thread after the DB commit so a slow push service
never holds up a save. Subscriptions the push service reports gone (404/410)
are deleted.
"""

import json
import logging
import threading

from django.conf import settings
from django.db import close_old_connections, transaction
from django.utils import timezone

log = logging.getLogger(__name__)

GONE_STATUSES = {404, 410}


def _payload(title: str, body: str, url: str, tag: str) -> str:
    return json.dumps({'title': title, 'body': body, 'url': url or '/', 'tag': tag or ''})


def send_now(user_ids, *, title: str, body: str = '', url: str = '', tag: str = '') -> int:
    """Send synchronously. Returns how many deliveries succeeded."""
    if not settings.PUSH_ENABLED or not user_ids:
        return 0
    from pywebpush import WebPushException, webpush

    from .models import PushSubscription

    data = _payload(title, body, url, tag)
    sent = 0
    for sub in PushSubscription.objects.filter(user_id__in=list(user_ids)):
        try:
            webpush(
                subscription_info={'endpoint': sub.endpoint, 'keys': {'p256dh': sub.p256dh, 'auth': sub.auth}},
                data=data,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={'sub': settings.VAPID_SUBJECT},
                ttl=6 * 3600,
                timeout=10,
            )
        except WebPushException as exc:
            status = getattr(getattr(exc, 'response', None), 'status_code', None)
            if status in GONE_STATUSES:
                sub.delete()
            else:
                log.warning('push failed (%s): %s', status, sub.endpoint[:60])
            continue
        except Exception:  # noqa: BLE001 — push is best-effort
            log.warning('push failed: %s', sub.endpoint[:60], exc_info=True)
            continue
        PushSubscription.objects.filter(pk=sub.pk).update(last_ok_at=timezone.now())
        sent += 1
    return sent


def _run(user_ids, kwargs):
    try:
        send_now(user_ids, **kwargs)
    finally:
        close_old_connections()


def send(user_ids, *, title: str, body: str = '', url: str = '', tag: str = '') -> None:
    """Queue a push for after commit; delivery happens off the request thread."""
    if not settings.PUSH_ENABLED:
        return
    ids = sorted({uid for uid in user_ids if uid})
    if not ids:
        return
    kwargs = {'title': title, 'body': body, 'url': url, 'tag': tag}

    def start():
        if getattr(settings, 'PUSH_SYNC', False):
            send_now(ids, **kwargs)
            return
        threading.Thread(target=_run, args=(ids, kwargs), daemon=True).start()

    transaction.on_commit(start)
