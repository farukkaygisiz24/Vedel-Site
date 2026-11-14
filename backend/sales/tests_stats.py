from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import Customer
from stock.models import Category, Product

from .models import Party, Sale, SaleLine
from .stats import period_label, year_summary


class YearSummaryTests(TestCase):
    def setUp(self):
        self.user = Customer.objects.create_user(
            username='st-sales', password='pass-word', is_staff=True, role=Customer.ROLE_SALES
        )
        self.party = Party.objects.create(
            kind=Party.KIND_REAL, number='CUSTC8801', first_name='Ali', last_name='Kaya',
            phone='05550000021', created_by=self.user,
        )
        klima = Category.objects.create(
            name='Klima Stats', slug='klima-stats', sku_prefix='KS', is_klima=True, created_by=self.user
        )
        copper = Category.objects.create(
            name='Bakır Stats', slug='bakir-stats', sku_prefix='BS', is_copper_pipe=True, created_by=self.user
        )

        def product(sku, name, kind='', category=klima, is_device=True):
            return Product.objects.create(
                sku=sku, brand='Mitsubishi', name=name, category=category, is_device=is_device,
                device_kind=kind, stock_qty=Decimal('50.00'), created_by=self.user,
            )

        self.split = product('KS1', 'SRK25', Product.KIND_SPLIT)
        self.outdoor = product('KS2', 'SCM60', Product.KIND_MULTI_OUTDOOR)
        self.indoor = product('KS3', 'SRK20', Product.KIND_MULTI_INDOOR)
        self.legacy = product('KS4', 'Eski kart')
        self.pipe = product('BS1', 'Bakır boru', category=copper, is_device=False)

    def sale(self, number, when, *lines):
        sale = Sale.objects.create(
            number=number, date=when, party=self.party, work_type=Sale.WORK_DEVICE, vat_mode=Sale.VAT_NONE,
            subtotal=Decimal('0.00'), vat_total=Decimal('0.00'), grand_total=Decimal('0.00'),
            created_by=self.user, updated_by=self.user,
        )
        total = Decimal('0.00')
        for item, qty, price in lines:
            amount = Decimal(qty) * Decimal(price)
            SaleLine.objects.create(
                sale=sale, product=item, qty=Decimal(qty), unit_price=Decimal(price), vat_rate=Decimal('0'),
                line_net=amount, line_vat=Decimal('0.00'), line_total=amount,
            )
            total += amount
        sale.grand_total = sale.subtotal = total
        sale.save(update_fields=['grand_total', 'subtotal'])
        return sale

    def test_counts_split_and_multi_outdoor_as_systems(self):
        self.sale('SAL20260901', date(2026, 3, 1), (self.split, 2, 1000), (self.pipe, 10, 50))
        self.sale('SAL20260902', date(2026, 4, 1), (self.outdoor, 1, 3000), (self.indoor, 3, 800))
        self.sale('SAL20260903', date(2026, 5, 1), (self.legacy, 1, 900))
        self.sale('SAL20250901', date(2025, 5, 1), (self.split, 5, 1000))

        summary = year_summary(2026)

        self.assertEqual(summary.sale_count, 3)
        self.assertEqual(summary.split_systems, 3)
        self.assertEqual(summary.multi_systems, 1)
        self.assertEqual(summary.systems, 4)
        self.assertEqual(summary.revenue, Decimal('8800.00'))
        self.assertEqual([item.qty for item in summary.top], [3, 2, 1])
        self.assertEqual(summary.top[0].name, 'Mitsubishi · SRK20')
        self.assertNotIn('Bakır boru', [item.name for item in summary.top])

    def test_legacy_line_next_to_multi_outdoor_is_an_indoor(self):
        self.sale('SAL20260904', date(2026, 6, 1), (self.outdoor, 1, 3000), (self.legacy, 2, 500))
        summary = year_summary(2026)
        self.assertEqual((summary.split_systems, summary.multi_systems), (0, 1))

    def test_sales_page_shows_summary(self):
        today = date.today()
        self.sale(f'SAL{today.year}0905', today, (self.split, 1, 1000))
        self.client.force_login(self.user)
        response = self.client.get(reverse('portal-sales'))
        self.assertContains(response, 'Satılan sistem')
        self.assertContains(response, 'Split 1 · Multi 0')


class PeriodLabelTests(TestCase):
    def test_labels(self):
        today = date(2026, 11, 14)
        self.assertEqual(period_label(date(2026, 1, 1), today, today), '1 Oca – 14 Kas')
        self.assertEqual(period_label(date(2025, 12, 1), date(2026, 1, 31), today), '1 Ara 2025 – 31 Oca 2026')
        self.assertEqual(period_label(None, None, today), 'Tüm zamanlar')
        self.assertEqual(period_label(date(2026, 8, 1), None, today), '1 Ağu – bugün')

    def test_customers_page_labels(self):
        user = Customer.objects.create_user(
            username='st-sales2', password='pass-word', is_staff=True, role=Customer.ROLE_SALES
        )
        self.client.force_login(user)
        response = self.client.get(reverse('portal-sales-customers'))
        self.assertContains(response, 'Açık bakiye')
        self.assertContains(response, 'İş hacmi')
        self.assertContains(response, 'Borçlu müşteri')
        self.assertNotContains(response, 'Güncel bakiyeler')
