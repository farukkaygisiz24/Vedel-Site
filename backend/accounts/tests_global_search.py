from datetime import time, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Customer
from crew.models import CrewMember
from sales.models import Party, Sale
from service.models import Job


class GlobalSearchTests(TestCase):
    def setUp(self):
        self.admin = Customer.objects.create_superuser(username='gs-admin', password='pass-word')
        self.sales = Customer.objects.create_user(
            username='gs-sales', password='pass-word', is_staff=True, role=Customer.ROLE_SALES
        )
        self.lead = Customer.objects.create_user(
            username='gs-lead', password='pass-word', is_staff=True, role=Customer.ROLE_SERVICE_LEAD
        )
        self.tech_user = Customer.objects.create_user(
            username='gs-tech', password='pass-word', is_staff=True, role=Customer.ROLE_SERVICE
        )
        self.tech = CrewMember.objects.create(
            number='CRWGS1', first_name='Selim', last_name='Saha', phone='05550000011',
            user=self.tech_user, created_by=self.admin,
        )
        self.party = Party.objects.create(
            kind=Party.KIND_LEGAL, number='CUSTC7701', company_name='MAKİN MÜHENDİSLİK',
            phone='05550000012', city='BURSA', created_by=self.admin,
        )
        self.other = Party.objects.create(
            kind=Party.KIND_REAL, number='CUSTR7702', first_name='Ayşe', last_name='Demir',
            phone='05550000013', created_by=self.admin,
        )
        today = timezone.localdate()
        Sale.objects.create(
            number='SAL20990001', date=today, party=self.party, work_type=Sale.WORK_DEVICE,
            vat_mode=Sale.VAT_NONE, subtotal=Decimal('100.00'), vat_total=Decimal('0.00'),
            grand_total=Decimal('100.00'), created_by=self.admin, updated_by=self.admin,
        )
        self.mine = Job.objects.create(
            number='SRV20990001', date=today + timedelta(days=1), time=time(10, 0), party=self.party,
            status=Job.STATUS_OPEN, assignee=self.tech, created_by=self.admin, updated_by=self.admin,
        )
        Job.objects.create(
            number='SRV20990002', date=today + timedelta(days=1), time=time(11, 0), party=self.other,
            status=Job.STATUS_PENDING, created_by=self.admin, updated_by=self.admin,
        )

    def search(self, user, q):
        self.client.force_login(user)
        response = self.client.get(reverse('portal-search'), {'q': q})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        return {group['key']: [item['title'] for item in group['items']] for group in data['groups']}, data

    def test_turkish_i_matches_and_groups_for_admin(self):
        groups, _ = self.search(self.admin, 'makin')
        self.assertEqual(groups['parties'], ['MAKİN MÜHENDİSLİK'])
        self.assertEqual(groups['sales'], ['SAL20990001'])
        self.assertEqual(groups['jobs'], ['SRV20990001'])

    def test_short_query_returns_nothing(self):
        groups, data = self.search(self.admin, 'm')
        self.assertEqual(groups, {})
        self.assertEqual(data['groups'], [])

    def test_sales_user_has_no_job_group(self):
        groups, _ = self.search(self.sales, 'makin')
        self.assertIn('parties', groups)
        self.assertIn('sales', groups)
        self.assertNotIn('jobs', groups)

    def test_lead_sees_pending_jobs_too(self):
        groups, _ = self.search(self.lead, 'srv2099')
        self.assertEqual(sorted(groups['jobs']), ['SRV20990001', 'SRV20990002'])
        groups, data = self.search(self.lead, 'makin')
        self.assertEqual(data['groups'][0]['items'][0]['url'], self.party.get_absolute_url())

    def test_field_user_sees_only_own_open_jobs_with_field_url(self):
        groups, data = self.search(self.tech_user, 'srv2099')
        self.assertEqual(groups, {'jobs': ['SRV20990001']})
        self.assertEqual(data['groups'][0]['items'][0]['url'], self.mine.get_field_url())

    def test_requires_login(self):
        response = self.client.get(reverse('portal-search'), {'q': 'makin'})
        self.assertEqual(response.status_code, 302)
