from datetime import date
from decimal import Decimal

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase, override_settings
from django.urls import path

from accounts.consumers import PortalConsumer
from accounts.models import Customer
from accounts.realtime import GROUP_SALES, GROUP_SERVICE, GROUP_STOCK, groups_for, user_group
from sales.models import Party, Sale

IN_MEMORY = {'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}}
APP = URLRouter([path('ws/portal/', PortalConsumer.as_asgi())])


@override_settings(CHANNEL_LAYERS=IN_MEMORY)
class LiveSocketTests(TransactionTestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='live-lead', password='pass-word', is_staff=True, role=Customer.ROLE_SERVICE_LEAD
        )
        self.sales = Customer.objects.create_user(
            username='live-sales', password='pass-word', is_staff=True, role=Customer.ROLE_SALES
        )

    def _comm(self, user):
        comm = WebsocketCommunicator(APP, '/ws/portal/')
        comm.scope['user'] = user
        return comm

    def test_groups_by_role(self):
        self.assertEqual(
            groups_for(self.lead),
            [user_group(self.lead.pk), GROUP_SALES, GROUP_SERVICE, GROUP_STOCK],
        )
        self.assertEqual(groups_for(self.sales), [user_group(self.sales.pk), GROUP_SALES, GROUP_STOCK])

    async def test_anonymous_rejected(self):
        from django.contrib.auth.models import AnonymousUser

        comm = self._comm(AnonymousUser())
        connected, code = await comm.connect()
        self.assertFalse(connected)
        self.assertEqual(code, 4401)

    async def test_sale_event_reaches_sales_user_not_service_only(self):
        comm = self._comm(self.sales)
        connected, _ = await comm.connect()
        self.assertTrue(connected)

        @sync_to_async
        def make_sale():
            party = Party.objects.create(
                kind=Party.KIND_REAL, number='CUSTLIVE1', first_name='Canlı', last_name='Test',
                phone='05550007788', address='Test', created_by=self.lead,
            )
            return Sale.objects.create(
                number='SALLIVE01', date=date.today(), party=party, work_type=Sale.WORK_DEVICE,
                vat_mode=Sale.VAT_NONE, grand_total=Decimal('10.00'),
                created_by=self.lead, updated_by=self.lead,
            )

        sale = await make_sale()
        msg = await comm.receive_json_from(timeout=2)
        self.assertEqual(msg['kind'], 'sales')
        self.assertEqual(msg['actor'], self.lead.pk)
        self.assertEqual(msg['text'], 'Yeni satış: SALLIVE01')
        self.assertEqual(msg['id'], sale.pk)

        # The sales user also gets a notification-center entry on their own channel.
        note = await comm.receive_json_from(timeout=2)
        self.assertEqual(note['kind'], 'notification')
        self.assertEqual(note['notification']['title'], 'Yeni satış fişi · SALLIVE01')

        # A maintenance event goes to the service group only.
        await get_channel_layer().group_send(GROUP_SERVICE, {'type': 'live.event', 'kind': 'maintenance'})
        self.assertTrue(await comm.receive_nothing(timeout=0.3))
        await comm.disconnect()

    async def test_ping_pong(self):
        comm = self._comm(self.lead)
        await comm.connect()
        await comm.send_json_to({'type': 'ping'})
        self.assertEqual(await comm.receive_json_from(timeout=2), {'type': 'pong'})
        await comm.disconnect()
