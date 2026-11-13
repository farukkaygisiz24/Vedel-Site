from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import Customer
from stock.models import Category, Product
from stock.services import (
    DEFAULT_CATEGORY_SLUG,
    SERVICE_CATEGORY_SLUG,
    create_category,
    default_category,
    delete_category,
)


class ProductSearchSaleFiltersTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='stock-search-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.merkez = default_category(self.lead)
        self.klima = create_category(name='Euroform', prefix='EF', user=self.lead, is_klima=True)
        self.merkez_item = Product.objects.create(
            sku='STK-0003',
            name='SC-BIKN2-E',
            category=self.merkez,
            unit='ADET',
            vat_rate=Decimal('20.00'),
            created_by=self.lead,
        )
        self.split_item = Product.objects.create(
            sku='EF-0001',
            name='Split Ünite',
            category=self.klima,
            unit='ADET',
            vat_rate=Decimal('20.00'),
            is_device=True,
            device_kind=Product.KIND_SPLIT,
            created_by=self.lead,
        )
        self.client.force_login(self.lead)

    def _search(self, **params):
        return self.client.get(
            reverse('portal-stock'),
            params,
            HTTP_ACCEPT='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

    def test_merkez_visible_under_klima_brand(self):
        page = self._search(q='STK-0003', device_family='split', category_id=str(self.klima.pk))
        self.assertEqual(page.status_code, 200)
        data = page.json()
        self.assertTrue(data['ok'])
        skus = {item['sku'] for item in data['results']}
        self.assertIn('STK-0003', skus)

    def test_klima_brand_still_lists_split_devices(self):
        page = self._search(q='EF-0001', device_family='split', category_id=str(self.klima.pk))
        self.assertEqual(page.status_code, 200)
        skus = {item['sku'] for item in page.json()['results']}
        self.assertIn('EF-0001', skus)


class CategoryDeleteTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='stock-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.empty = create_category(name='Bosch', prefix='BOS', user=self.lead)

    def test_delete_empty_category(self):
        delete_category(item=self.empty)
        self.assertFalse(Category.objects.filter(pk=self.empty.pk).exists())

    def test_cannot_delete_category_with_products(self):
        Product.objects.create(
            sku='BOS-0001',
            name='Deneme',
            category=self.empty,
            unit='ADET',
            vat_rate=Decimal('20.00'),
            created_by=self.lead,
        )
        with self.assertRaisesMessage(ValueError, 'Bu kategoride 1 ürün var. Önce ürünleri silin.'):
            delete_category(item=self.empty)
        self.assertTrue(Category.objects.filter(pk=self.empty.pk).exists())

    def test_cannot_delete_system_category(self):
        merkez = create_category(name='Merkez Depo', prefix='STK', user=self.lead)
        self.assertEqual(merkez.slug, DEFAULT_CATEGORY_SLUG)
        with self.assertRaisesMessage(ValueError, 'Bu kategori silinemez.'):
            delete_category(item=merkez)

    def test_office_deletes_empty_category(self):
        self.client.force_login(self.lead)
        page = self.client.get(reverse('portal-stock'), {'category': self.empty.slug})
        self.assertContains(page, 'id="delete-stock-settings"')
        self.assertNotContains(page, 'id="s-cat-list"')
        self.assertNotContains(page, 'id="s-cat-new"')
        self.assertNotContains(page, 'Yeni kategori')
        deleted = self.client.post(
            reverse('portal-stock'),
            {'action': 'delete_category', 'id': str(self.empty.pk)},
            HTTP_ACCEPT='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(deleted.status_code, 200)
        self.assertTrue(deleted.json()['ok'])
        self.assertFalse(Category.objects.filter(pk=self.empty.pk).exists())

    def test_office_keeps_service_category(self):
        service = create_category(name='Klima Servis', prefix='KS', user=self.lead)
        self.assertEqual(service.slug, SERVICE_CATEGORY_SLUG)
        self.client.force_login(self.lead)
        blocked = self.client.post(
            reverse('portal-stock'),
            {'action': 'delete_category', 'id': str(service.pk)},
            HTTP_ACCEPT='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(blocked.status_code, 400)
        self.assertEqual(blocked.json()['error'], 'Bu kategori silinemez.')
        self.assertTrue(Category.objects.filter(pk=service.pk).exists())


class DeviceSerialTrackingTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='serial-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.merkez = default_category(self.lead)
        self.klima = create_category(name='Euroform', prefix='EF', user=self.lead, is_klima=True)

    def test_merkez_product_without_serial(self):
        from stock.services import apply_device_fields

        product = Product.objects.create(
            sku='STK-0099',
            name='KNX Aparat',
            category=self.merkez,
            unit='ADET',
            vat_rate=Decimal('20.00'),
            created_by=self.lead,
        )
        apply_device_fields(product, {'tracks_serial': '0'})
        product.save(update_fields=['is_device', 'device_kind', 'outdoor', 'outdoor_name'])
        product.refresh_from_db()
        self.assertFalse(product.is_device)
        self.assertEqual(product.device_kind, Product.KIND_NONE)

    def test_merkez_product_with_serial(self):
        from stock.services import apply_device_fields

        product = Product.objects.create(
            sku='STK-0100',
            name='Hava Perdesi',
            category=self.merkez,
            unit='ADET',
            vat_rate=Decimal('20.00'),
            created_by=self.lead,
        )
        apply_device_fields(product, {'tracks_serial': '1'})
        product.save(update_fields=['is_device', 'device_kind', 'outdoor', 'outdoor_name'])
        product.refresh_from_db()
        self.assertTrue(product.is_device)
        self.assertEqual(product.device_kind, Product.KIND_NONE)

    def test_klima_still_requires_family(self):
        from stock.services import apply_device_fields

        product = Product.objects.create(
            sku='EF-0099',
            name='Split',
            category=self.klima,
            unit='ADET',
            vat_rate=Decimal('20.00'),
            created_by=self.lead,
        )
        with self.assertRaisesMessage(ValueError, 'Split veya multi seçin.'):
            apply_device_fields(product, {'tracks_serial': '1', 'device_kind': ''})

    def test_new_form_asks_serial_question(self):
        self.client.force_login(self.lead)
        page = self.client.get(reverse('portal-stock-new'))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Seri no takibi')
        self.assertContains(page, 'name="tracks_serial"')
        self.assertContains(page, 'Kumanda, KNX')

    def test_sale_line_skips_accessory_on_device_sale(self):
        from sales.models import Party, Sale, SaleLine
        from service.services import sale_line_is_device

        accessory = Product.objects.create(
            sku='STK-0003',
            name='Kumanda',
            category=self.merkez,
            unit='ADET',
            vat_rate=Decimal('20.00'),
            is_device=False,
            created_by=self.lead,
        )
        curtain = Product.objects.create(
            sku='STK-0009',
            name='Hava Perdesi',
            category=self.merkez,
            unit='ADET',
            vat_rate=Decimal('20.00'),
            is_device=True,
            created_by=self.lead,
        )
        party = Party.objects.create(
            kind=Party.KIND_REAL,
            number='P-SER-1',
            first_name='Ali',
            last_name='Test',
            phone='05550001122',
            address='Test',
            created_by=self.lead,
        )
        sale = Sale.objects.create(
            number='S-TEST-1',
            date=date(2026, 1, 15),
            party=party,
            work_type=Sale.WORK_DEVICE,
            vat_mode=Sale.VAT_NONE,
            subtotal=Decimal('0.00'),
            vat_total=Decimal('0.00'),
            grand_total=Decimal('0.00'),
            created_by=self.lead,
            updated_by=self.lead,
        )
        zero = Decimal('0.00')
        acc_line = SaleLine.objects.create(
            sale=sale,
            product=accessory,
            qty=Decimal('1'),
            unit_price=zero,
            cost_price=zero,
            vat_rate=zero,
            line_net=zero,
            line_vat=zero,
            line_total=zero,
        )
        curtain_line = SaleLine.objects.create(
            sale=sale,
            product=curtain,
            qty=Decimal('1'),
            unit_price=zero,
            cost_price=zero,
            vat_rate=zero,
            line_net=zero,
            line_vat=zero,
            line_total=zero,
        )
        self.assertFalse(sale_line_is_device(acc_line, sale))
        self.assertTrue(sale_line_is_device(curtain_line, sale))


class CopperCategoryTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='copper-cat-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )

    def test_klima_included_meters_and_copper_flag(self):
        klima = create_category(
            name='Mitsubishi Heavy',
            prefix='MHI',
            user=self.lead,
            is_klima=True,
            included_copper_meters='5',
        )
        self.assertEqual(klima.included_copper_meters, Decimal('5.00'))
        self.assertFalse(klima.is_copper_pipe)
        copper = create_category(
            name='Bakır Test',
            prefix='BKT',
            user=self.lead,
            is_copper_pipe=True,
        )
        self.assertTrue(copper.is_copper_pipe)
        self.assertEqual(copper.included_copper_meters, Decimal('0.00'))

    def test_protected_copper_category_keeps_flag(self):
        from stock.services import copper_category, update_category

        copper = copper_category(self.lead)
        update_category(item=copper, name=copper.name, prefix=copper.sku_prefix, is_copper_pipe=False)
        copper.refresh_from_db()
        self.assertTrue(copper.is_copper_pipe)

    def test_included_meters_capped(self):
        with self.assertRaisesMessage(ValueError, 'en fazla 1000'):
            create_category(
                name='Huge Klima',
                prefix='HGK',
                user=self.lead,
                is_klima=True,
                included_copper_meters='5000',
            )

    def test_klima_and_copper_mutually_exclusive(self):
        with self.assertRaisesMessage(ValueError, 'Klima ve bakır boru aynı kategoride olamaz.'):
            create_category(
                name='Bad Mix',
                prefix='BAD',
                user=self.lead,
                is_klima=True,
                is_copper_pipe=True,
            )
