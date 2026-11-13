"""Live portal updates over websockets (Django Channels).

Writes in sales / service / stock broadcast a tiny event after the DB commit.
Office browsers listen on /ws/portal/ and quietly refresh the list they show.
Broadcast failures (e.g. Redis down) never break the save itself.
"""

import logging

from asgiref.sync import async_to_sync
from django.db import transaction

log = logging.getLogger(__name__)

# Event kind -> groups that may receive it (by role).
GROUP_SALES = 'live.sales'
GROUP_SERVICE = 'live.service'
GROUP_STOCK = 'live.stock'

KIND_GROUPS = {
    'sales': (GROUP_SALES,),
    'jobs': (GROUP_SERVICE,),
    'stock': (GROUP_STOCK,),
    'maintenance': (GROUP_SERVICE,),
}


def groups_for(user) -> list[str]:
    groups = []
    if getattr(user, 'can_sales', False):
        groups.append(GROUP_SALES)
    if getattr(user, 'can_service_lead', False):
        groups.append(GROUP_SERVICE)
    if getattr(user, 'can_stock', False):
        groups.append(GROUP_STOCK)
    return groups


def _send(kind: str, payload: dict) -> None:
    from channels.layers import get_channel_layer

    layer = get_channel_layer()
    if layer is None:
        return
    message = {'type': 'live.event', 'kind': kind, **payload}
    for group in KIND_GROUPS.get(kind, ()):
        try:
            async_to_sync(layer.group_send)(group, message)
        except Exception:  # noqa: BLE001 — live updates are best-effort
            log.warning('live broadcast failed: %s', kind, exc_info=True)
            return


def broadcast(kind: str, *, actor_id=None, text: str = '', obj_id=None) -> None:
    """Queue a live event to send once the current transaction commits."""
    payload = {'actor': actor_id, 'text': text, 'id': obj_id}
    transaction.on_commit(lambda: _send(kind, payload))
