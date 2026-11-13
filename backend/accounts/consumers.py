from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .realtime import groups_for


class PortalConsumer(AsyncJsonWebsocketConsumer):
    """One socket per office tab. Receives live.event messages for the user's roles."""

    groups_joined: list[str]

    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated or not user.is_staff and not user.is_superuser:
            await self.close(code=4401)
            return
        self.groups_joined = await database_sync_to_async(groups_for)(user)
        if not self.groups_joined:
            await self.close(code=4403)
            return
        for group in self.groups_joined:
            await self.channel_layer.group_add(group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        for group in getattr(self, 'groups_joined', []):
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get('type') == 'ping':
            await self.send_json({'type': 'pong'})

    async def live_event(self, event):
        await self.send_json(
            {
                'type': 'live',
                'kind': event.get('kind'),
                'actor': event.get('actor'),
                'text': event.get('text') or '',
                'id': event.get('id'),
            }
        )
