from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import Customer
from crew.models import CrewMember
from service.models import Job, JobLine
from service.services import adjust_closed_job, close_job

from .models import Party, Payment, PaymentAllocation, Sale
from .services import add_job_payment, add_party_payment, add_payment, delete_payment, party_from_post


class PartyPaymentTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='pay-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.member = CrewMember.objects.create(
            number='CRWPAY1',
            first_name='Ömer',
            last_name='Teknisyen',
            phone='05551112233',
            created_by=self.lead,
        )
        self.party = Party.objects.create(
            kind=Party.KIND_REAL,
            number='CUSTC9001',
            first_name='Ebubekir',
            last_name='Test',
            phone='05550001122',
            address='Test mah',
            created_by=self.lead,
        )
        today = date.today()
        self.sale = self._sale('SAL20269001', Decimal('40.00'), today - timedelta(days=2))
        self.job = self._closed_job('SRV20269001', Decimal('80.00'), today - timedelta(days=1))

    def _sale(self, number, total, when):
        return Sale.objects.create(
            number=number,
            date=when,
            party=self.party,
            work_type=Sale.WORK_DEVICE,
            vat_mode=Sale.VAT_NONE,
            subtotal=total,
            vat_total=Decimal('0.00'),
            grand_total=total,
            created_by=self.lead,
            updated_by=self.lead,
        )

    def _closed_job(self, number, total, when):
        job = Job.objects.create(
            number=number,
            date=when,
            party=self.party,
            vat_mode=Job.VAT_NONE,
            status=Job.STATUS_SUBMITTED,
            subtotal=total,
            vat_total=Decimal('0.00'),
            grand_total=total,
            assignee=self.member,
            created_by=self.lead,
            updated_by=self.lead,
        )
        JobLine.objects.create(
            job=job,
            kind=JobLine.KIND_LABOR,
            description='Bakım',
            qty=Decimal('1.00'),
            unit_price=total,
            vat_rate=Decimal('0.00'),
            line_net=total,
            line_vat=Decimal('0.00'),
            line_total=total,
        )
        return close_job(job=job, user=self.lead)

    def _pay_post(self, amount, method='cash'):
        return {
            'pay_method': method,
            'pay_amount': str(amount),
            'pay_date': date.today().isoformat(),
        }

    def test_fifo_splits_oldest_open_first(self):
        payment = add_party_payment(party=self.party, user=self.lead, post=self._pay_post('100'))
        self.assertEqual(payment.amount, Decimal('100.00'))
        self.assertEqual(payment.party_id, self.party.pk)
        self.assertEqual(self.sale.paid_total, Decimal('40.00'))
        self.assertEqual(self.job.paid_total, Decimal('60.00'))
        self.assertEqual(self.sale.remaining, Decimal('0.00'))
        self.assertEqual(self.job.remaining, Decimal('20.00'))
        allocs = list(payment.allocations.order_by('id'))
        self.assertEqual(len(allocs), 2)
        self.assertEqual(allocs[0].sale_id, self.sale.pk)
        self.assertEqual(allocs[0].amount, Decimal('40.00'))
        self.assertEqual(allocs[1].job_id, self.job.pk)
        self.assertEqual(allocs[1].amount, Decimal('60.00'))

    def test_sale_slip_payment_still_works(self):
        payment = add_payment(sale=self.sale, user=self.lead, post=self._pay_post('25'))
        self.assertEqual(payment.party_id, self.party.pk)
        self.assertEqual(self.sale.paid_total, Decimal('25.00'))
        self.assertEqual(self.sale.remaining, Decimal('15.00'))
        self.assertEqual(PaymentAllocation.objects.filter(sale=self.sale).count(), 1)
        self.client.force_login(self.lead)
        page = self.client.get(self.sale.get_absolute_url())
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, '25,00')
        self.assertContains(page, 'Ödeme ekle')

    def test_job_payment_shows_on_job_and_customer_tab(self):
        add_job_payment(job=self.job, user=self.lead, post=self._pay_post('15'))
        self.assertEqual(self.job.paid_total, Decimal('15.00'))
        self.client.force_login(self.lead)
        job_page = self.client.get(self.job.get_absolute_url())
        self.assertEqual(job_page.status_code, 200)
        self.assertContains(job_page, 'Ödeme detayları')
        self.assertContains(job_page, '15,00')
        cust = self.client.get(self.party.get_absolute_url() + '?tab=payments')
        self.assertEqual(cust.status_code, 200)
        self.assertContains(cust, 'Cihazlar')
        self.assertContains(cust, 'Satışlar')
        self.assertContains(cust, 'Servis işleri')
        self.assertContains(cust, 'Ödemeler')
        self.assertContains(cust, 'Tahsilat ekle')
        self.assertContains(cust, self.job.number)
        self.assertContains(cust, '15,00')

    def test_delete_removes_whole_receipt(self):
        payment = add_party_payment(party=self.party, user=self.lead, post=self._pay_post('100'))
        delete_payment(user=self.lead, post={'payment_id': str(payment.pk)}, party=self.party)
        self.assertFalse(Payment.objects.filter(pk=payment.pk).exists())
        self.assertFalse(PaymentAllocation.objects.filter(payment_id=payment.pk).exists())
        self.assertEqual(self.sale.paid_total, Decimal('0.00'))
        self.assertEqual(self.job.paid_total, Decimal('0.00'))

    def test_overpay_rejected(self):
        with self.assertRaisesMessage(ValueError, 'Kalan borç'):
            add_party_payment(party=self.party, user=self.lead, post=self._pay_post('200'))

    def test_customer_payments_post_fifo(self):
        self.client.force_login(self.lead)
        page = self.client.get(self.party.get_absolute_url() + '?tab=payments')
        self.assertContains(page, 'id="open-pay"')
        self.assertContains(page, 'id="pay-modal"')
        self.assertContains(page, 'en eski açık bakiyeden')
        response = self.client.post(
            self.party.get_absolute_url() + '?tab=payments',
            self._pay_post('100') | {'action': 'payment'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.sale.paid_total, Decimal('40.00'))
        self.assertEqual(self.job.paid_total, Decimal('60.00'))
        self.assertEqual(self.job.remaining, Decimal('20.00'))

    def test_customer_tabs_and_job_columns(self):
        self.client.force_login(self.lead)
        jobs = self.client.get(self.party.get_absolute_url() + '?tab=jobs')
        self.assertContains(jobs, 'Tahsil')
        self.assertContains(jobs, 'Kalan')
        self.assertContains(jobs, self.job.number)
        devices = self.client.get(self.party.get_absolute_url())
        self.assertContains(devices, 'role="tablist"')
        self.assertNotContains(devices, 'class="steps"')
        self.assertContains(devices, 'data-tab-panel="devices"')
        self.assertContains(devices, 'data-tab-panel="sales"')
        self.assertContains(devices, 'data-tab-panel="jobs"')
        self.assertContains(devices, 'data-tab-panel="payments"')


class PartyCityDistrictRequiredTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='party-city-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )

    def _post(self, **extra):
        data = {
            'kind': Party.KIND_REAL,
            'first_name': 'Ali',
            'last_name': 'Veli',
            'phone': '05551112233',
            'address': 'Test mah',
            'city': 'Bursa',
            'district': 'Nilüfer',
        }
        data.update(extra)
        return data

    def test_party_requires_city(self):
        with self.assertRaisesMessage(ValueError, 'İl zorunlu.'):
            party_from_post(self._post(city=''), self.lead)

    def test_party_requires_district(self):
        with self.assertRaisesMessage(ValueError, 'İlçe zorunlu.'):
            party_from_post(self._post(district=''), self.lead)

    def test_party_saves_city_and_district(self):
        party = party_from_post(self._post(), self.lead)
        party.number = 'CUSTC9901'
        party.save()
        party.refresh_from_db()
        self.assertEqual(party.city, 'BURSA')
        self.assertEqual(party.district, 'NİLÜFER')

    def test_party_modal_marks_city_district_required(self):
        self.client.force_login(self.lead)
        page = self.client.get(reverse('portal-sales-customers'))
        body = page.content.decode()
        self.assertIn('id="m_city"', body)
        self.assertIn('id="m_district"', body)
        self.assertRegex(body, r'id="m_city"[^>]*\srequired')
        self.assertRegex(body, r'id="m_district"[^>]*\srequired')
        self.assertIn('data-city-district', body)
        self.assertIn('data-city-pick', body)
        self.assertIn('data-district-pick', body)
        self.assertIn('tr-cities-data', body)
        self.assertIn('BURSA', body)
        self.assertIn('data-default-city="BURSA"', body)

    def test_legal_tax_no_accepts_11_digits(self):
        party = party_from_post(
            self._post(
                kind=Party.KIND_LEGAL,
                company_name='Ali Veli Ltd',
                tax_no='12345678901',
                first_name='Ali',
                last_name='Veli',
            ),
            self.lead,
        )
        self.assertEqual(party.tax_no, '12345678901')

    def test_legal_tax_no_rejects_wrong_length(self):
        with self.assertRaisesMessage(ValueError, 'Vergi kimlik no 10 veya 11 haneli olmalıdır.'):
            party_from_post(
                self._post(
                    kind=Party.KIND_LEGAL,
                    company_name='Ali Veli Ltd',
                    tax_no='12345',
                    first_name='Ali',
                    last_name='Veli',
                ),
                self.lead,
            )
