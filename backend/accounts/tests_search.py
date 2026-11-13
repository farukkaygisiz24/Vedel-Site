from django.test import SimpleTestCase, TestCase

from accounts.models import Customer
from accounts.search import q_search
from sales.models import Party
from sales.views import _party_queryset


class QSearchLookupTests(SimpleTestCase):
    def test_q_search_expands_turkish_i_variants(self):
        from accounts.search import tr_i_variants

        variants = tr_i_variants('makin')
        self.assertIn('makin', variants)
        self.assertIn('makın', variants)
        self.assertIn('makİn', variants)
        q = q_search('makin', 'company_name')
        self.assertEqual(len(q.children), len(variants))

    def test_q_search_blank_is_empty(self):
        self.assertFalse(bool(q_search('  ')))
        self.assertFalse(bool(q_search('')))


class TurkishPartySearchTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='search-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.party = Party.objects.create(
            kind=Party.KIND_LEGAL,
            number='CUSTC6111999',
            company_name='MAKİN MÜHENDİSLİK',
            first_name='Onur',
            last_name='Bayindir',
            phone='0 (532) 000 00 00',
            address='Test',
            city='BURSA',
            district='NİLÜFER',
            created_by=self.lead,
        )

    def test_ascii_makin_finds_turkish_company(self):
        hits = list(_party_queryset('makin').values_list('company_name', flat=True))
        self.assertIn('MAKİN MÜHENDİSLİK', hits)

    def test_customers_page_search(self):
        self.client.force_login(self.lead)
        page = self.client.get('/sales/customers/', {'q': 'makin'})
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'MAKİN MÜHENDİSLİK')
