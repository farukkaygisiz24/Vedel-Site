from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.dashboard import dashboard_context, month_bounds, sales_revenue, service_revenue
from accounts.models import Customer
from sales.models import Party, Sale
from service.models import Device, Job
from stock.models import Category, Product

TODAY = date(2026, 3, 15)


class DashboardBase(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='dash-lead', password='pass-word', is_staff=True, role=Customer.ROLE_SERVICE_LEAD
        )
        self.sales = Customer.objects.create_user(
            username='dash-sales', password='pass-word', is_staff=True, role=Customer.ROLE_SALES
        )
        self.party = Party.objects.create(
            kind=Party.KIND_REAL,
            number='CUSTDASH1',
            first_name='Dash',
            last_name='Müşteri',
            phone='05550001122',
            address='Test',
            created_by=self.lead,
        )
        self.klima = Category.objects.create(
            name='Dash Klima', slug='dash-klima', sku_prefix='DKL', is_klima=True, created_by=self.lead
        )
        self.copper = Category.objects.create(
            name='Dash Bakır', slug='dash-bakir', sku_prefix='DBK', is_copper_pipe=True, created_by=self.lead
        )
        self.device = Product.objects.create(
            sku='DKL-0001', brand='X', name='Split Kritik', category=self.klima, is_device=True,
            stock_qty=Decimal('1.00'), alert_on=True, alert_qty=Decimal('2.00'), created_by=self.lead,
        )
        Product.objects.create(
            sku='DKL-0002', brand='X', name='Split Bol', category=self.klima, is_device=True,
            stock_qty=Decimal('20.00'), alert_on=True, alert_qty=Decimal('2.00'), created_by=self.lead,
        )
        self.pipe = Product.objects.create(
            sku='DBK-0001', brand='X', name='Bakır Boru Dash', category=self.copper, unit='MT',
            stock_qty=Decimal('-4.00'), created_by=self.lead,
        )

    def _sale(self, number, day, total):
        return Sale.objects.create(
            number=number, date=day, party=self.party, work_type=Sale.WORK_DEVICE,
            vat_mode=Sale.VAT_NONE, grand_total=Decimal(total), created_by=self.lead, updated_by=self.lead,
        )

    def _job(self, number, day, status, total='0', sale=None):
        return Job.objects.create(
            number=number, date=day, party=self.party, status=status, sale=sale,
            grand_total=Decimal(total), created_by=self.lead, updated_by=self.lead,
        )


class RevenueTests(DashboardBase):
    def test_month_bounds_wrap_year(self):
        self.assertEqual(
            month_bounds(date(2026, 1, 9)), (date(2025, 12, 1), date(2026, 1, 1), date(2026, 2, 1))
        )
        self.assertEqual(
            month_bounds(date(2026, 12, 31)), (date(2026, 11, 1), date(2026, 12, 1), date(2027, 1, 1))
        )

    def test_sales_this_and_previous_month(self):
        self._sale('SALD0001', date(2026, 3, 1), '1000')
        self._sale('SALD0002', date(2026, 3, 31), '500')
        self._sale('SALD0003', date(2026, 2, 28), '1000')
        self._sale('SALD0004', date(2026, 4, 1), '9999')
        rev = sales_revenue(TODAY)
        self.assertEqual(rev.current.total, Decimal('1500'))
        self.assertEqual(rev.current.count, 2)
        self.assertEqual(rev.previous.total, Decimal('1000'))
        self.assertEqual(rev.delta_pct, 50)
        self.assertEqual(rev.current.label, 'Mart 2026')

    def test_service_counts_only_closed_jobs_without_sale(self):
        sale = self._sale('SALD0010', TODAY, '700')
        self._job('SRVD0001', TODAY, Job.STATUS_CLOSED, '300')
        self._job('SRVD0002', TODAY, Job.STATUS_OPEN, '400')
        self._job('SRVD0003', TODAY, Job.STATUS_CLOSED, '700', sale=sale)
        rev = service_revenue(TODAY)
        self.assertEqual(rev.current.total, Decimal('300'))
        self.assertEqual(rev.current.count, 1)
        self.assertIsNone(rev.delta_pct)


class DashboardRoleTests(DashboardBase):
    def test_sales_user_sees_sales_and_device_stock_only(self):
        ctx = dashboard_context(self.sales, TODAY)
        self.assertIn('sales_revenue', ctx)
        self.assertEqual([p.sku for p in ctx['device_alerts']], ['DKL-0001'])
        for key in ('service_revenue', 'copper_items', 'missed_jobs', 'due_devices'):
            self.assertNotIn(key, ctx)

    def test_lead_sees_everything(self):
        self._job('SRVD0100', TODAY - timedelta(days=2), Job.STATUS_OPEN)
        self._job('SRVD0101', TODAY + timedelta(days=2), Job.STATUS_OPEN)
        Device.objects.create(
            party=self.party, name='Salon klima', interval_months=6,
            next_due=TODAY - timedelta(days=1), created_by=self.lead,
        )
        Device.objects.create(
            party=self.party, name='Oda klima', interval_months=12,
            next_due=TODAY + timedelta(days=60), created_by=self.lead,
        )
        ctx = dashboard_context(self.lead, TODAY)
        self.assertIn('sales_revenue', ctx)
        self.assertIn('service_revenue', ctx)
        self.assertEqual(ctx['missed_count'], 1)
        self.assertEqual(ctx['due_overdue_count'], 1)
        self.assertEqual(ctx['due_soon_count'], 0)
        self.assertEqual([p.sku for p in ctx['copper_items']], ['DBK-0001'])

    def test_page_renders_per_role(self):
        self.client.force_login(self.sales)
        page = self.client.get(reverse('portal-dashboard'))
        self.assertContains(page, 'Kritik cihaz stoğu')
        self.assertNotContains(page, 'Bakır boru</p>')
        self.assertNotContains(page, 'Gidilmeyen işler')
        self.assertEqual(page['Cache-Control'], 'no-store, max-age=0')
        self.client.force_login(self.lead)
        page = self.client.get(reverse('portal-dashboard'))
        self.assertContains(page, 'Gidilmeyen işler')
        self.assertContains(page, 'Bakır boru</p>')
        self.assertContains(page, 'Servis ·')
