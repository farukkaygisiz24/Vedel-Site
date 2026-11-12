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

    def test_merkez_product_visible_with_split_family(self):
        page = self._search(q='STK-0003', device_family='split', category_id=str(self.merkez.pk))
        self.assertEqual(page.status_code, 200)
        data = page.json()
        self.assertTrue(data['ok'])
        skus = {item['sku'] for item in data['results']}
        self.assertIn('STK-0003', skus)

    def test_klima_category_keeps_split_filter(self):
        page = self._search(q='STK-0003', device_family='split', category_id=str(self.klima.pk))
        self.assertEqual(page.status_code, 200)
        skus = {item['sku'] for item in page.json()['results']}
        self.assertNotIn('STK-0003', skus)
        page2 = self._search(q='EF-0001', device_family='split', category_id=str(self.klima.pk))
        skus2 = {item['sku'] for item in page2.json()['results']}
        self.assertIn('EF-0001', skus2)


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
