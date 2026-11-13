from datetime import date, time, timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Sum
from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Customer
from crew.models import CrewMember
from sales.models import Party, Sale, SaleLine
from sales.views import _organic_closed_jobs
from stock.models import Category, Product, StockMovement
from sales.services import delete_sale, line_amounts, next_sale_number
from stock.services import MOUNT_CATEGORY_SLUG, MOUNT_SKU_PREFIX, SERVICE_LABOR_SKU

from .models import Device, Job, JobLine, JobSoldUnit, JobSoldUnitMaterial, JobSoldUnitPhoto
from .services import (
    activate_sale_mount,
    adjust_closed_job,
    apply_sold_units,
    close_job,
    confirm_job,
    ensure_sold_packs,
    relabel_mount_job,
    sale_mount_preview_rows,
    save_field_job,
    save_job,
    schedule_sale_job,
)


class FieldMultiGroupTests(TestCase):
    def setUp(self):
        self.user = Customer.objects.create_user(
            username='field-tech',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        self.member = CrewMember.objects.create(
            number='CRWTEST1',
            first_name='Saha',
            last_name='Teknisyen',
            phone='05551112233',
            user=self.user,
            created_by=self.user,
        )
        party = Party.objects.create(
            kind=Party.KIND_REAL,
            number='PTEST1',
            first_name='Ali',
            last_name='Test',
            phone='05550001122',
            address='Test mah',
            created_by=self.user,
        )
        sale = Sale.objects.create(
            number='STEST1',
            date=date.today(),
            party=party,
            work_type=Sale.WORK_DEVICE,
            vat_mode=Sale.VAT_PLUS,
            created_by=self.user,
            updated_by=self.user,
        )
        category = Category.objects.create(
            name='Klima Test',
            slug='klima-test',
            sku_prefix='KT',
            is_klima=True,
            created_by=self.user,
        )
        indoor = Product.objects.create(
            sku='KTIN1',
            brand='Mitsubishi',
            name='SRK25ZS-W',
            category=category,
            is_device=True,
            device_kind=Product.KIND_MULTI_INDOOR,
            created_by=self.user,
        )
        outdoor = Product.objects.create(
            sku='KTOUT1',
            brand='Mitsubishi',
            name='SCM125ZS-W',
            category=category,
            is_device=True,
            device_kind=Product.KIND_MULTI_OUTDOOR,
            created_by=self.user,
        )
        zero = Decimal('0.00')
        SaleLine.objects.create(
            sale=sale,
            product=indoor,
            qty=Decimal('4.00'),
            unit_price=zero,
            cost_price=zero,
            vat_rate=Decimal('20.00'),
            line_net=zero,
            line_vat=zero,
            line_total=zero,
        )
        SaleLine.objects.create(
            sale=sale,
            product=outdoor,
            qty=Decimal('2.00'),
            unit_price=zero,
            cost_price=zero,
            vat_rate=Decimal('20.00'),
            line_net=zero,
            line_vat=zero,
            line_total=zero,
        )
        self.job = Job.objects.create(
            number='SRV20990001',
            date=date.today(),
            party=party,
            sale=sale,
            status=Job.STATUS_OPEN,
            assignee=self.member,
            created_by=self.user,
            updated_by=self.user,
        )
        ensure_sold_packs(self.job)

    def test_field_job_shows_group_picks_and_saves_assignment(self):
        self.client.force_login(self.user)
        url = reverse('portal-field-job', kwargs={'number': self.job.number})
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)
        body = page.content.decode()
        self.assertIn('Multi gruplar', body)
        self.assertIn('Grup 1', body)
        self.assertIn('Grup 2', body)
        units = list(JobSoldUnit.objects.filter(job=self.job).order_by('id'))
        packs = list(self.job.sold_packs.filter(kind='multi').order_by('sort', 'id'))
        self.assertEqual(len(units), 4)
        self.assertEqual(len(packs), 2)
        self.assertTrue(all(unit.pack_id is None for unit in units))
        payload = {
            'action': 'save',
            'notes': '',
            f'indoor_pack_{units[0].pk}': str(packs[0].pk),
            f'indoor_pack_{units[1].pk}': str(packs[0].pk),
            f'indoor_pack_{units[2].pk}': str(packs[1].pk),
            f'indoor_pack_{units[3].pk}': str(packs[1].pk),
            f'unit_room_{units[0].pk}': 'salon',
            f'unit_serial_{units[0].pk}': 'sn-a',
            f'pack_outdoor_serial_{packs[0].pk}': 'out-1',
            f'pack_outdoor_serial_{packs[1].pk}': 'out-2',
        }
        saved = self.client.post(url, payload)
        self.assertEqual(saved.status_code, 200)
        self.assertContains(saved, 'en az 4 görsel')
        units = list(JobSoldUnit.objects.filter(job=self.job).order_by('id'))
        packs = list(self.job.sold_packs.filter(kind='multi').order_by('sort', 'id'))
        self.assertEqual(units[0].pack_id, packs[0].pk)
        self.assertEqual(units[1].pack_id, packs[0].pk)
        self.assertEqual(units[2].pack_id, packs[1].pk)
        self.assertEqual(units[3].pack_id, packs[1].pk)
        self.assertEqual(units[0].room, 'SALON')
        self.assertEqual(units[0].serial, 'SN-A')
        packs[0].refresh_from_db()
        packs[1].refresh_from_db()
        self.assertEqual(packs[0].outdoor_serial, 'OUT-1')
        self.assertEqual(packs[1].outdoor_serial, 'OUT-2')

    def test_save_requires_every_indoor_in_a_group(self):
        units = list(JobSoldUnit.objects.filter(job=self.job).order_by('id'))
        packs = list(self.job.sold_packs.filter(kind='multi').order_by('sort', 'id'))
        post = {
            f'indoor_pack_{units[0].pk}': str(packs[0].pk),
            f'indoor_pack_{units[1].pk}': '',
            f'indoor_pack_{units[2].pk}': str(packs[1].pk),
            f'indoor_pack_{units[3].pk}': str(packs[1].pk),
        }
        with self.assertRaisesMessage(ValueError, 'Her iç üniteyi bir dış ünite grubuna bağlayın.'):
            save_field_job(user=self.user, job=self.job, post=post)

    def test_apply_sold_units_moves_indoor_between_groups(self):
        units = list(JobSoldUnit.objects.filter(job=self.job).order_by('id'))
        packs = list(self.job.sold_packs.filter(kind='multi').order_by('sort', 'id'))
        apply_sold_units(
            job=self.job,
            post={
                f'indoor_pack_{units[0].pk}': str(packs[0].pk),
                f'indoor_pack_{units[1].pk}': str(packs[0].pk),
                f'indoor_pack_{units[2].pk}': str(packs[1].pk),
                f'indoor_pack_{units[3].pk}': str(packs[1].pk),
            },
        )
        apply_sold_units(
            job=self.job,
            post={
                f'indoor_pack_{units[0].pk}': str(packs[1].pk),
                f'indoor_pack_{units[1].pk}': str(packs[0].pk),
                f'indoor_pack_{units[2].pk}': str(packs[1].pk),
                f'indoor_pack_{units[3].pk}': str(packs[1].pk),
            },
        )
        units[0].refresh_from_db()
        self.assertEqual(units[0].pack_id, packs[1].pk)
        self.assertEqual(packs[0].units.count(), 1)
        self.assertEqual(packs[1].units.count(), 3)


class FieldMountMaterialTests(TestCase):
    def setUp(self):
        self.user = Customer.objects.create_user(
            username='field-mount',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        self.member = CrewMember.objects.create(
            number='CRWTEST2',
            first_name='Saha',
            last_name='Montaj',
            phone='05551112233',
            user=self.user,
            created_by=self.user,
        )
        party = Party.objects.create(
            kind=Party.KIND_REAL,
            number='PTEST2',
            first_name='Ali',
            last_name='Test',
            phone='05550001122',
            address='Test mah',
            created_by=self.user,
        )
        sale = Sale.objects.create(
            number='STEST2',
            date=date.today(),
            party=party,
            work_type=Sale.WORK_DEVICE,
            vat_mode=Sale.VAT_PLUS,
            created_by=self.user,
            updated_by=self.user,
        )
        mount = Category.objects.create(
            name='Klima Montaj Malzemesi',
            slug=MOUNT_CATEGORY_SLUG,
            sku_prefix=MOUNT_SKU_PREFIX,
            created_by=self.user,
        )
        self.user.stock_categories.add(mount)
        self.pipe = Product.objects.create(
            sku='KMM-0099',
            brand='Cantaş',
            name='3/8 1/4 BAKIR BORU',
            category=mount,
            unit='MT',
            stock_qty=Decimal('40.00'),
            created_by=self.user,
        )
        indoor = Product.objects.create(
            sku='KTIN2',
            brand='Mitsubishi',
            name='SRK25ZS-W',
            category=mount,
            is_device=True,
            device_kind=Product.KIND_SPLIT,
            outdoor_name='SRC25ZS-W',
            created_by=self.user,
        )
        zero = Decimal('0.00')
        SaleLine.objects.create(
            sale=sale,
            product=indoor,
            qty=Decimal('1.00'),
            unit_price=zero,
            cost_price=zero,
            vat_rate=Decimal('20.00'),
            line_net=zero,
            line_vat=zero,
            line_total=zero,
        )
        self.job = Job.objects.create(
            number='SRV20990002',
            date=date.today(),
            party=party,
            sale=sale,
            status=Job.STATUS_OPEN,
            assignee=self.member,
            created_by=self.user,
            updated_by=self.user,
        )
        ensure_sold_packs(self.job)

    def test_field_job_lists_mount_stock_and_saves_qty(self):
        self.client.force_login(self.user)
        page = self.client.get(reverse('portal-field-job', kwargs={'number': self.job.number}))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Montaj malzemesi')
        self.assertContains(page, 'Klima Montaj Malzemesi')
        products = self.client.get(reverse('portal-field-products'), {'mount': '1'})
        self.assertEqual(products.status_code, 200)
        rows = products.json()['results']
        self.assertTrue(any(item['sku'] == 'KMM-0099' for item in rows))
        self.assertTrue(all(item['sku'].startswith('KMM-') for item in rows))
        pipe_row = next(item for item in rows if item['sku'] == 'KMM-0099')
        self.assertEqual(pipe_row['unit'], 'MT')
        saved = self.client.post(
            reverse('portal-field-job', kwargs={'number': self.job.number}),
            {
                'action': 'save',
                'field_mat_present': '1',
                'field_mat_product': str(self.pipe.pk),
                'field_mat_qty': '5,5',
            },
        )
        self.assertEqual(saved.status_code, 200)
        self.assertContains(saved, 'en az 4 görsel')
        material = JobSoldUnitMaterial.objects.get(pack__job=self.job, product=self.pipe)
        self.assertEqual(material.qty, Decimal('5.50'))
        self.pipe.refresh_from_db()
        self.assertEqual(self.pipe.stock_qty, Decimal('34.50'))

    def test_field_mount_hides_stock_shortage(self):
        self.pipe.stock_qty = Decimal('0.00')
        self.pipe.save(update_fields=['stock_qty'])
        self.client.force_login(self.user)
        saved = self.client.post(
            reverse('portal-field-job', kwargs={'number': self.job.number}),
            {
                'action': 'save',
                'field_mat_present': '1',
                'field_mat_product': str(self.pipe.pk),
                'field_mat_qty': '1',
            },
        )
        self.assertEqual(saved.status_code, 200)
        self.assertNotContains(saved, 'yetersiz stok')
        self.assertNotContains(saved, 'elde')
        material = JobSoldUnitMaterial.objects.get(pack__job=self.job, product=self.pipe)
        self.assertEqual(material.qty, Decimal('1.00'))
        self.pipe.refresh_from_db()
        self.assertEqual(self.pipe.stock_qty, Decimal('-1.00'))

    def test_field_mount_lead_does_not_see_stock_shortage(self):
        self.user.role = Customer.ROLE_SERVICE_LEAD
        self.user.save(update_fields=['role'])
        self.pipe.stock_qty = Decimal('0.00')
        self.pipe.save(update_fields=['stock_qty'])
        self.client.force_login(self.user)
        saved = self.client.post(
            reverse('portal-field-job', kwargs={'number': self.job.number}),
            {
                'action': 'save',
                'field_mat_present': '1',
                'field_mat_product': str(self.pipe.pk),
                'field_mat_qty': '1',
            },
        )
        self.assertEqual(saved.status_code, 200)
        self.assertNotContains(saved, 'yetersiz stok')
        self.assertNotContains(saved, 'elde')
        self.pipe.refresh_from_db()
        self.assertEqual(self.pipe.stock_qty, Decimal('-1.00'))

    def test_field_mount_save_does_not_double_cut_stock(self):
        self.client.force_login(self.user)
        payload = {
            'action': 'save',
            'field_mat_present': '1',
            'field_mat_product': str(self.pipe.pk),
            'field_mat_qty': '2',
        }
        url = reverse('portal-field-job', kwargs={'number': self.job.number})
        first = self.client.post(url, payload)
        self.assertEqual(first.status_code, 200)
        second = self.client.post(url, payload)
        self.assertEqual(second.status_code, 200)
        self.pipe.refresh_from_db()
        self.assertEqual(self.pipe.stock_qty, Decimal('38.00'))
        self.assertEqual(
            StockMovement.objects.filter(job=self.job, product=self.pipe).count(),
            1,
        )

    def test_field_mount_rejects_products_outside_mount_category(self):
        other = Category.objects.create(
            name='Merkez Depo',
            slug='merkez-depo',
            sku_prefix='STK',
            created_by=self.user,
        )
        part = Product.objects.create(
            sku='STK-0001',
            name='Yedek parça',
            category=other,
            stock_qty=Decimal('10.00'),
            created_by=self.user,
        )
        with self.assertRaisesMessage(ValueError, 'Montaj malzemesi bulunamadı.'):
            save_field_job(
                user=self.user,
                job=self.job,
                post={
                    'field_mat_present': '1',
                    'field_mat_product': str(part.pk),
                    'field_mat_qty': '1',
                },
            )


class FieldServiceMaterialTests(TestCase):
    def setUp(self):
        self.user = Customer.objects.create_user(
            username='field-service',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        self.member = CrewMember.objects.create(
            number='CRWTEST3',
            first_name='Saha',
            last_name='Servis',
            phone='05551112233',
            user=self.user,
            created_by=self.user,
        )
        party = Party.objects.create(
            kind=Party.KIND_REAL,
            number='PTEST3',
            first_name='Ayşe',
            last_name='Test',
            phone='05550001122',
            address='Test mah',
            created_by=self.user,
        )
        merkez = Category.objects.create(
            name='Merkez Depo',
            slug='merkez-depo',
            sku_prefix='STK',
            created_by=self.user,
        )
        demontaj = Category.objects.create(
            name='Klima Demontaj Malzemesi',
            slug='klima-demontaj-malzemesi',
            sku_prefix='KDM',
            created_by=self.user,
        )
        klima = Category.objects.create(
            name='Mitsubishi Heavy Industries',
            slug='mitsubishi-heavy-industries',
            sku_prefix='MHI',
            is_klima=True,
            created_by=self.user,
        )
        self.part = Product.objects.create(
            sku='STK-0100',
            name='Yedek parça',
            category=merkez,
            stock_qty=Decimal('12.00'),
            sale_price=Decimal('100.00'),
            created_by=self.user,
        )
        self.hose = Product.objects.create(
            sku='KDM-0001',
            name='Tahliye hortumu',
            category=demontaj,
            unit='AD',
            stock_qty=Decimal('8.00'),
            created_by=self.user,
        )
        self.klima_part = Product.objects.create(
            sku='MHI-0099',
            name='İç ünite filtre',
            category=klima,
            stock_qty=Decimal('4.00'),
            created_by=self.user,
        )
        self.job = Job.objects.create(
            number='SRV20990003',
            date=date.today(),
            party=party,
            status=Job.STATUS_OPEN,
            assignee=self.member,
            created_by=self.user,
            updated_by=self.user,
        )

    def test_field_job_lists_non_klima_stock_and_saves_part(self):
        self.client.force_login(self.user)
        page = self.client.get(reverse('portal-field-job', kwargs={'number': self.job.number}))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Kalemler')
        self.assertContains(page, 'Malzeme ekle')
        self.assertContains(page, 'Depo')
        self.assertNotContains(page, 'Parça ekle')
        self.assertNotContains(page, 'İşçilik ekle')
        products = self.client.get(reverse('portal-field-products'), {'service': '1'})
        self.assertEqual(products.status_code, 200)
        rows = products.json()['results']
        skus = {item['sku'] for item in rows}
        self.assertEqual(skus, {'STK-0100', 'KDM-0001'})
        hose = next(item for item in rows if item['sku'] == 'KDM-0001')
        self.assertEqual(hose['unit'], 'AD')
        saved = self.client.post(
            reverse('portal-field-job', kwargs={'number': self.job.number}),
            {
                'action': 'save',
                'field_lines_present': '1',
                'kind': ['part'],
                'product_id': [str(self.part.pk)],
                'description': ['Yedek parça'],
                'qty': ['2'],
                'unit_price': ['100'],
                'cost_price': [''],
                'vat_rate': ['20'],
            },
        )
        self.assertEqual(saved.status_code, 302)
        lines = list(JobLine.objects.filter(job=self.job).order_by('id'))
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].kind, JobLine.KIND_PART)
        self.assertEqual(lines[0].product_id, self.part.pk)
        self.assertEqual(lines[0].qty, Decimal('2.00'))

    def test_field_service_rejects_klima_category_products(self):
        post = QueryDict(mutable=True)
        post.update({'action': 'save', 'field_lines_present': '1'})
        post.setlist('kind', ['part'])
        post.setlist('product_id', [str(self.klima_part.pk)])
        post.setlist('description', [''])
        post.setlist('qty', ['1'])
        post.setlist('unit_price', ['0'])
        with self.assertRaisesMessage(ValueError, 'Servis malzemesi bulunamadı.'):
            save_field_job(user=self.user, job=self.job, post=post)


class FieldHomeRecentDoneTests(TestCase):
    def setUp(self):
        self.user = Customer.objects.create_user(
            username='field-home',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        self.member = CrewMember.objects.create(
            number='CRWHOME1',
            first_name='Saha',
            last_name='Liste',
            phone='05551112233',
            user=self.user,
            created_by=self.user,
        )
        self.other = CrewMember.objects.create(
            number='CRWHOME2',
            first_name='Başka',
            last_name='Teknisyen',
            phone='05551112234',
            created_by=self.user,
        )
        self.party = Party.objects.create(
            kind=Party.KIND_REAL,
            number='PHOME1',
            first_name='Ali',
            last_name='Tamam',
            phone='05550001122',
            address='Test mah',
            created_by=self.user,
        )

    def _job(self, number, *, status, assignee=None, submitted_at=None, when=None):
        job = Job.objects.create(
            number=number,
            date=when or date.today(),
            party=self.party,
            status=status,
            assignee=assignee or self.member,
            submitted_at=submitted_at,
            created_by=self.user,
            updated_by=self.user,
        )
        return job

    def test_field_home_lists_last_five_completed_jobs(self):
        now = timezone.now()
        self._job('SRV20991100', status=Job.STATUS_OPEN)
        self._job(
            'SRV20991101',
            status=Job.STATUS_SUBMITTED,
            submitted_at=now - timedelta(days=6),
        )
        newest = []
        for offset in range(5):
            newest.append(
                self._job(
                    f'SRV2099111{offset}',
                    status=Job.STATUS_CLOSED if offset == 0 else Job.STATUS_SUBMITTED,
                    submitted_at=now - timedelta(hours=offset),
                    when=date.today() - timedelta(days=offset),
                )
            )
        self._job(
            'SRV20991199',
            status=Job.STATUS_SUBMITTED,
            assignee=self.other,
            submitted_at=now,
        )
        self.client.force_login(self.user)
        page = self.client.get(reverse('portal-field'))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Yarın açık iş yok.')
        self.assertContains(page, 'Son tamamlanan')
        body = page.content.decode()
        recent = body.split('Son tamamlanan', 1)[1]
        self.assertIn('SRV20991110', recent)
        self.assertIn('SRV20991114', recent)
        self.assertNotIn('SRV20991101', recent)
        self.assertNotIn('SRV20991100', recent)
        self.assertNotIn('SRV20991199', recent)
        self.assertLess(recent.find('SRV20991110'), recent.find('SRV20991114'))


class AssignAllFieldTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='pool-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.tech = Customer.objects.create_user(
            username='pool-tech',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        self.other_user = Customer.objects.create_user(
            username='pool-tech-2',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        self.member = CrewMember.objects.create(
            number='CRWPOOL1',
            first_name='Samet',
            last_name='Aydın',
            phone='05551112233',
            user=self.tech,
            created_by=self.lead,
        )
        self.other = CrewMember.objects.create(
            number='CRWPOOL2',
            first_name='Enes',
            last_name='Yılmaz',
            phone='05551112234',
            user=self.other_user,
            created_by=self.lead,
        )
        self.party = Party.objects.create(
            kind=Party.KIND_REAL,
            number='PPOOL1',
            first_name='Ali',
            last_name='Havuz',
            phone='05550001122',
            address='Test mah',
            created_by=self.lead,
        )

    def _pool_job(self, number='SRV20992200', **extra):
        data = {
            'number': number,
            'date': date.today(),
            'party': self.party,
            'status': Job.STATUS_OPEN,
            'assign_all': True,
            'created_by': self.lead,
            'updated_by': self.lead,
        }
        data.update(extra)
        return Job.objects.create(**data)

    def test_pool_job_shows_on_every_field_home(self):
        job = self._pool_job()
        for user in (self.tech, self.other_user):
            self.client.force_login(user)
            page = self.client.get(reverse('portal-field'))
            self.assertEqual(page.status_code, 200)
            self.assertContains(page, job.number)
            field = self.client.get(job.get_field_url())
            self.assertEqual(field.status_code, 200)
            self.assertTrue(field.context['can_edit'])

    def test_personal_job_stays_private(self):
        job = self._pool_job(number='SRV20992201', assign_all=False, assignee=self.member)
        self.client.force_login(self.other_user)
        home = self.client.get(reverse('portal-field'))
        self.assertNotContains(home, job.number)
        field = self.client.get(job.get_field_url())
        self.assertEqual(field.status_code, 404)

    def test_submitter_becomes_assignee(self):
        job = self._pool_job()
        post = QueryDict(mutable=True)
        post.update({'action': 'submit', 'notes': ''})
        save_field_job(user=self.other_user, job=job, post=post)
        job.refresh_from_db()
        self.assertEqual(job.status, Job.STATUS_SUBMITTED)
        self.assertEqual(job.assignee_id, self.other.pk)
        self.assertEqual(job.submitted_by_id, self.other_user.pk)
        self.assertTrue(job.assign_all)
        self.assertEqual(job.assignee_label, 'Enes Yılmaz')
        self.client.force_login(self.tech)
        self.assertEqual(self.client.get(job.get_field_url()).status_code, 404)
        self.client.force_login(self.other_user)
        done = self.client.get(reverse('portal-field'))
        self.assertContains(done, job.number)
        self.client.force_login(self.lead)
        page = self.client.get(job.get_absolute_url())
        self.assertContains(page, 'Enes Yılmaz')


class OfficeJobOpenTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='office-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.tech = Customer.objects.create_user(
            username='office-tech',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        self.member = CrewMember.objects.create(
            number='CRWTEST9',
            first_name='Samet',
            last_name='Aydın',
            phone='05551112233',
            user=self.tech,
            created_by=self.lead,
        )
        self.party = Party.objects.create(
            kind=Party.KIND_REAL,
            number='PTEST9',
            first_name='Ali',
            last_name='Test',
            phone='05550001122',
            address='Test mah',
            created_by=self.lead,
        )
        cat = Category.objects.create(
            name='Klima Servis',
            slug='klima-servis',
            sku_prefix='KS',
            created_by=self.lead,
        )
        spare = Category.objects.create(
            name='Yedek',
            slug='yedek-parca',
            sku_prefix='STK',
            created_by=self.lead,
        )
        self.labor = Product.objects.create(
            sku=SERVICE_LABOR_SKU,
            name='Demontaj - Montaj',
            category=cat,
            unit='AD',
            vat_rate=Decimal('20.00'),
            sale_price=Decimal('1500.00'),
            created_by=self.lead,
        )
        self.labor_alt = Product.objects.create(
            sku='KS-0001',
            name='Bakım',
            category=cat,
            unit='AD',
            vat_rate=Decimal('20.00'),
            sale_price=Decimal('800.00'),
            created_by=self.lead,
        )
        self.part = Product.objects.create(
            sku='STK-0200',
            name='Yedek vida',
            category=spare,
            unit='AD',
            vat_rate=Decimal('20.00'),
            sale_price=Decimal('80.00'),
            stock_qty=Decimal('10.00'),
            created_by=self.lead,
        )

    def _open_post(self, **extra):
        data = {
            'action': 'save',
            'party_mode': 'existing',
            'party_id': str(self.party.pk),
            'date': date.today().isoformat(),
            'assignee_id': str(self.member.pk),
            'device_mode': 'none',
            'notes': 'Demontaj montaj',
        }
        data.update(extra)
        return data

    def test_new_job_form_hides_new_device_and_lines(self):
        self.client.force_login(self.lead)
        page = self.client.get(reverse('portal-service-job-new'))
        body = page.content.decode()
        self.assertEqual(page.status_code, 200)
        self.assertIn('Cihaz yok', body)
        self.assertIn('İş ara', body)
        self.assertIn('İş seç', body)
        self.assertIn('Personel seç', body)
        self.assertIn('Seçilmedi', body)
        self.assertIn('Demontaj - Montaj', body)
        self.assertIn('Bakım', body)
        self.assertIn('Kaydetmek için personel seçin.', body)
        self.assertIn('data-pick-id="all"', body)
        self.assertIn('Hepsi', body)
        self.assertEqual(page.context['assignee_id'], 'all')
        self.assertEqual(page.context['assignee_name'], 'Hepsi')
        self.assertNotIn('name="vat_mode"', body)
        self.assertNotIn('KDV yok', body)
        self.assertNotIn('data-pick-hay="Atanmadı"', body)
        self.assertNotIn('Yeni cihaz', body)
        self.assertNotIn('İşçilik ekle', body)
        self.assertNotIn('id="job-lines"', body)

    def test_office_requires_assignee(self):
        self.client.force_login(self.lead)
        resp = self.client.post(
            reverse('portal-service-job-new'),
            self._open_post(assignee_id=''),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Personel seçin.')
        self.assertFalse(Job.objects.filter(party=self.party).exists())

    def test_office_saves_assign_all(self):
        self.client.force_login(self.lead)
        resp = self.client.post(
            reverse('portal-service-job-new'),
            self._open_post(assignee_id='all'),
        )
        self.assertEqual(resp.status_code, 302)
        job = Job.objects.get(party=self.party)
        self.assertTrue(job.assign_all)
        self.assertIsNone(job.assignee_id)
        self.assertEqual(job.assignee_label, 'Hepsi')

    def test_office_saves_without_work(self):
        self.client.force_login(self.lead)
        resp = self.client.post(reverse('portal-service-job-new'), self._open_post())
        self.assertEqual(resp.status_code, 302)
        job = Job.objects.get(party=self.party)
        self.assertEqual(resp['Location'], f"{reverse('portal-service')}?day={job.date.isoformat()}")
        self.assertEqual(job.status, Job.STATUS_OPEN)
        self.assertEqual(job.notes, 'Demontaj montaj')
        self.assertIsNone(job.device_id)
        self.assertEqual(job.lines.count(), 0)
        self.assertEqual(job.grand_total, Decimal('0.00'))

    def test_office_saves_selected_work(self):
        self.client.force_login(self.lead)
        resp = self.client.post(
            reverse('portal-service-job-new'),
            self._open_post(work_id=str(self.labor.pk)),
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('portal-service'), resp['Location'])
        job = Job.objects.get(party=self.party)
        lines = list(job.lines.select_related('product'))
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].kind, JobLine.KIND_LABOR)
        self.assertEqual(lines[0].product_id, self.labor.pk)
        self.assertEqual(lines[0].qty, Decimal('1.00'))
        self.assertEqual(lines[0].unit_price, Decimal('1500.00'))
        self.assertEqual(lines[0].vat_rate, Decimal('0.00'))
        self.assertEqual(job.vat_mode, Job.VAT_NONE)
        self.assertEqual(job.grand_total, Decimal('1500.00'))
        self.assertEqual(job.assignee_id, self.member.pk)

    def test_seed_skips_when_already_present(self):
        self.client.force_login(self.lead)
        self.client.post(reverse('portal-service-job-new'), self._open_post(work_id=str(self.labor.pk)))
        job = Job.objects.get(party=self.party)
        self.client.post(job.get_absolute_url(), self._open_post(work_id=str(self.labor.pk)))
        self.assertEqual(job.lines.count(), 1)

    def test_change_work_replaces_labor(self):
        self.client.force_login(self.lead)
        self.client.post(reverse('portal-service-job-new'), self._open_post(work_id=str(self.labor.pk)))
        job = Job.objects.get(party=self.party)
        self.client.post(job.get_absolute_url(), self._open_post(work_id=str(self.labor_alt.pk)))
        line = job.lines.get()
        self.assertEqual(line.product_id, self.labor_alt.pk)
        self.assertEqual(line.unit_price, Decimal('800.00'))

    def test_vat_none_zeros_labor_vat(self):
        net, vat, total = line_amounts(Decimal('1'), Decimal('1500'), Decimal('20'), Job.VAT_NONE)
        self.assertEqual(net, Decimal('1500.00'))
        self.assertEqual(vat, Decimal('0.00'))
        self.assertEqual(total, Decimal('1500.00'))
        job = save_job(user=self.lead, post=self._open_post(work_id=str(self.labor.pk)))
        line = job.lines.get()
        self.assertEqual(job.vat_mode, Job.VAT_NONE)
        self.assertEqual(line.vat_rate, Decimal('0.00'))
        self.assertEqual(line.line_vat, Decimal('0.00'))
        self.assertEqual(line.line_total, Decimal('1500.00'))

    def _price_post(self, job, *, vat_mode, price, vat_rate=''):
        post = QueryDict(mutable=True)
        post.update(
            {
                'action': 'save',
                'party_mode': 'existing',
                'party_id': str(self.party.pk),
                'date': job.date.isoformat(),
                'assignee_id': str(self.member.pk),
                'device_mode': 'none',
                'vat_mode': vat_mode,
                'notes': job.notes,
            }
        )
        post.setlist('kind', ['labor'])
        post.setlist('product_id', [''])
        post.setlist('description', ['Demontaj - Montaj'])
        post.setlist('qty', ['1'])
        post.setlist('unit_price', [price])
        post.setlist('cost_price', ['0'])
        post.setlist('vat_rate', [vat_rate])
        return post

    def test_plus_vat_uses_twenty_on_empty_rate(self):
        job = save_job(user=self.lead, post=self._open_post(work_id=str(self.labor.pk)))
        save_job(user=self.lead, post=self._price_post(job, vat_mode=Job.VAT_PLUS, price='1000'), job=job)
        job.refresh_from_db()
        line = job.lines.get()
        self.assertEqual(job.vat_mode, Job.VAT_PLUS)
        self.assertEqual(line.vat_rate, Decimal('20.00'))
        self.assertEqual(line.line_net, Decimal('1000.00'))
        self.assertEqual(line.line_vat, Decimal('200.00'))
        self.assertEqual(line.line_total, Decimal('1200.00'))
        self.assertEqual(job.grand_total, Decimal('1200.00'))

    def test_included_vat_keeps_typed_total(self):
        job = save_job(user=self.lead, post=self._open_post(work_id=str(self.labor.pk)))
        save_job(user=self.lead, post=self._price_post(job, vat_mode=Job.VAT_INCLUDED, price='1200'), job=job)
        job.refresh_from_db()
        line = job.lines.get()
        self.assertEqual(job.vat_mode, Job.VAT_INCLUDED)
        self.assertEqual(line.vat_rate, Decimal('20.00'))
        self.assertEqual(line.line_net, Decimal('1000.00'))
        self.assertEqual(line.line_vat, Decimal('200.00'))
        self.assertEqual(line.line_total, Decimal('1200.00'))
        self.assertEqual(job.grand_total, Decimal('1200.00'))

    def test_field_hides_price_and_keeps_labor(self):
        job = save_job(user=self.lead, post=self._open_post(work_id=str(self.labor.pk)))
        self.client.force_login(self.tech)
        page = self.client.get(reverse('portal-field-job', kwargs={'number': job.number}))
        self.assertEqual(page.status_code, 200)
        rows = page.context['line_rows']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['kind'], JobLine.KIND_LABOR)
        self.assertNotIn('unit_price', rows[0])
        self.assertNotIn('cost_price', rows[0])
        self.assertContains(page, 'Demontaj - Montaj')
        self.assertNotContains(page, '1.500,00')
        post = QueryDict(mutable=True)
        post.update({'action': 'save', 'field_lines_present': '1', 'notes': job.notes})
        post.setlist('kind', ['part'])
        post.setlist('product_id', [str(self.part.pk)])
        post.setlist('description', [self.part.display_name])
        post.setlist('qty', ['1'])
        post.setlist('unit_price', [''])
        post.setlist('cost_price', [''])
        post.setlist('vat_rate', [''])
        save_field_job(user=self.tech, job=job, post=post)
        kinds = list(job.lines.order_by('kind').values_list('kind', 'product_id', 'unit_price'))
        self.assertEqual(len(kinds), 2)
        labor = job.lines.get(kind=JobLine.KIND_LABOR)
        part = job.lines.get(kind=JobLine.KIND_PART)
        self.assertEqual(labor.product_id, self.labor.pk)
        self.assertEqual(labor.unit_price, Decimal('1500.00'))
        self.assertEqual(part.product_id, self.part.pk)
        self.assertEqual(part.unit_price, Decimal('80.00'))

    def test_office_closes_submitted_job(self):
        job = save_job(user=self.lead, post=self._open_post(work_id=str(self.labor.pk)))
        job.status = Job.STATUS_SUBMITTED
        job.save(update_fields=['status'])
        self.client.force_login(self.lead)
        page = self.client.get(job.get_absolute_url())
        self.assertContains(page, 'İşçilik ekle')
        self.assertContains(page, 'id="job-lines"')
        self.assertContains(page, 'name="vat_mode"')
        self.assertContains(page, 'Servis fişi')
        self.assertContains(page, 'Yapılacak iş')
        self.assertContains(page, 'Kapat')
        self.assertNotContains(page, 'Kapat ve fişe dönüştür')
        self.assertContains(page, 'Ara toplam')
        self.assertContains(page, 'Genel toplam')
        self.assertContains(page, 'id="sum-vat"')
        self.assertContains(page, 'id="sum-cost"')
        self.assertNotContains(page, '1 · Müşteri')
        line = job.lines.get()
        closed = close_job(job=job, user=self.lead)
        self.assertEqual(closed.status, Job.STATUS_CLOSED)
        self.assertIsNone(closed.sale_id)
        self.assertEqual(closed.lines.get().description, line.description)
        self.assertEqual(
            _organic_closed_jobs(party=self.party).aggregate(s=Sum('grand_total'))['s'],
            Decimal('1500.00'),
        )

    def test_office_cannot_close_without_prices(self):
        job = save_job(user=self.lead, post=self._open_post(work_id=str(self.labor.pk)))
        job.status = Job.STATUS_SUBMITTED
        job.save(update_fields=['status'])
        post = self._price_post(job, vat_mode=Job.VAT_NONE, price='')
        post['action'] = 'close'
        with self.assertRaisesMessage(ValueError, 'Her kaleme satış fiyatı girin.'):
            save_job(user=self.lead, post=post, job=job)
        job.refresh_from_db()
        self.assertEqual(job.status, Job.STATUS_SUBMITTED)
        self.assertIsNone(job.sale_id)

    def test_office_cannot_close_before_submit(self):
        job = save_job(user=self.lead, post=self._open_post(work_id=str(self.labor.pk)))
        self.assertEqual(job.status, Job.STATUS_OPEN)
        with self.assertRaisesMessage(ValueError, 'Saha teslim etmeden iş kapatılamaz.'):
            close_job(job=job, user=self.lead)
        job.refresh_from_db()
        self.assertEqual(job.status, Job.STATUS_OPEN)
        self.assertIsNone(job.sale_id)

    def test_field_job_shows_assigned_work_to_do(self):
        job = save_job(user=self.lead, post=self._open_post(work_id=str(self.labor.pk)))
        self.client.force_login(self.tech)
        page = self.client.get(job.get_field_url())
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Yapılacak iş')
        self.assertContains(page, 'Ofisten atanan iş')
        self.assertNotContains(page, 'placeholder="Adet"')
        labor = next(row for row in page.context['line_rows'] if row['kind'] == JobLine.KIND_LABOR)
        self.assertEqual(labor['unit'], 'AD')
        self.assertEqual(labor['description'], 'Demontaj - Montaj')
        self.assertContains(page, 'mount-qty')
        products = self.client.get(reverse('portal-field-products'), {'service': '1'})
        skus = {item['sku'] for item in products.json()['results']}
        self.assertNotIn(SERVICE_LABOR_SKU, skus)
        self.assertNotIn('KS-0001', skus)
        self.assertIn('STK-0200', skus)

    def test_submitted_jobs_stay_on_week_and_inbox(self):
        job = save_job(user=self.lead, post=self._open_post(work_id=str(self.labor.pk)))
        post = QueryDict(mutable=True)
        post.update({'action': 'submit', 'field_lines_present': '1', 'notes': job.notes})
        post.setlist('kind', ['part'])
        post.setlist('product_id', [str(self.part.pk)])
        post.setlist('description', [self.part.display_name])
        post.setlist('qty', ['2'])
        post.setlist('unit_price', [''])
        post.setlist('cost_price', [''])
        post.setlist('vat_rate', [''])
        save_field_job(user=self.tech, job=job, post=post)
        job.refresh_from_db()
        self.assertEqual(job.status, Job.STATUS_SUBMITTED)
        self.assertIsNone(job.sale_id)
        labor = job.lines.get(kind=JobLine.KIND_LABOR)
        part = job.lines.get(kind=JobLine.KIND_PART)
        self.assertEqual(labor.product_id, self.labor.pk)
        self.assertEqual(labor.unit_price, Decimal('1500.00'))
        self.assertEqual(part.product_id, self.part.pk)
        self.assertEqual(part.qty, Decimal('2.00'))
        self.client.force_login(self.lead)
        page = self.client.get(reverse('portal-service'))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Teslim edilen işler')
        self.assertContains(page, 'Kontrol et')
        self.assertContains(page, job.number)
        week_ids = [item.pk for group in page.context['week_rows'] for item in group['jobs']]
        self.assertIn(job.pk, week_ids)
        self.assertContains(page, 'Teslim')
        self.assertEqual([item.pk for item in page.context['submitted']], [job.pk])
        form = self.client.get(job.get_absolute_url())
        self.assertTrue(form.context['office_close'])
        kinds = [row['kind'] for row in form.context['initial_lines']]
        self.assertCountEqual(kinds, [JobLine.KIND_LABOR, JobLine.KIND_PART])
        self.assertIn('unit_price', form.context['initial_lines'][0])
        closed = close_job(job=job, user=self.lead)
        self.assertEqual(closed.status, Job.STATUS_CLOSED)
        self.assertIsNone(closed.sale_id)
        self.assertEqual(closed.lines.count(), 2)
        self.assertEqual(closed.lines.get(kind=JobLine.KIND_LABOR).list_unit_price, Decimal('1500.00'))
        self.assertEqual(closed.list_grand, closed.grand_total)
        self.assertEqual(closed.discount_rate, Decimal('0.0000'))


class ClosedJobPaymentTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='adj-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.tech = Customer.objects.create_user(
            username='adj-tech',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        self.member = CrewMember.objects.create(
            number='CRWADJ1',
            first_name='Saha',
            last_name='Teknisyen',
            phone='05551112233',
            user=self.tech,
            created_by=self.lead,
        )
        self.party = Party.objects.create(
            kind=Party.KIND_REAL,
            number='CUSTC9002',
            first_name='Ali',
            last_name='Servis',
            phone='05550001122',
            address='Test mah',
            created_by=self.lead,
        )
        cat = Category.objects.create(
            name='Klima Servis',
            slug='klima-servis',
            sku_prefix='KS',
            created_by=self.lead,
        )
        self.labor = Product.objects.create(
            sku=SERVICE_LABOR_SKU,
            name='Demontaj - Montaj',
            category=cat,
            unit='AD',
            vat_rate=Decimal('20.00'),
            sale_price=Decimal('15.00'),
            created_by=self.lead,
        )

    def _closed_job(self, total=Decimal('15.00')):
        job = Job.objects.create(
            number='SRV20269002',
            date=date.today(),
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
            product=self.labor,
            description='Demontaj - Montaj',
            qty=Decimal('1.00'),
            unit_price=total,
            vat_rate=Decimal('0.00'),
            line_net=total,
            line_vat=Decimal('0.00'),
            line_total=total,
        )
        return close_job(job=job, user=self.lead)

    def test_discount_rescales_line_and_percent(self):
        job = self._closed_job()
        adjust_closed_job(
            job=job,
            user=self.lead,
            post={'vat_mode': Job.VAT_NONE, 'grand_total': '10'},
        )
        job.refresh_from_db()
        line = job.lines.get()
        self.assertEqual(job.status, Job.STATUS_CLOSED)
        self.assertIsNone(job.sale_id)
        self.assertEqual(job.grand_total, Decimal('10.00'))
        self.assertEqual(job.list_grand, Decimal('15.00'))
        self.assertEqual(job.discount_rate, Decimal('33.3333'))
        self.assertEqual(line.unit_price, Decimal('10.00'))
        self.assertEqual(line.list_unit_price, Decimal('15.00'))
        self.assertEqual(line.line_total, Decimal('10.00'))

    def test_vat_none_to_plus_then_manual_grand(self):
        job = self._closed_job()
        adjust_closed_job(job=job, user=self.lead, post={'vat_mode': Job.VAT_PLUS})
        job.refresh_from_db()
        self.assertEqual(job.list_grand, Decimal('18.00'))
        self.assertEqual(job.grand_total, Decimal('18.00'))
        self.assertEqual(job.vat_mode, Job.VAT_PLUS)
        adjust_closed_job(
            job=job,
            user=self.lead,
            post={'vat_mode': Job.VAT_PLUS, 'grand_total': '10'},
        )
        job.refresh_from_db()
        self.assertEqual(job.list_grand, Decimal('18.00'))
        self.assertEqual(job.grand_total, Decimal('10.00'))
        self.assertEqual(job.discount_rate, Decimal('44.4444'))
        self.assertEqual(job.status, Job.STATUS_CLOSED)

    def test_grand_below_paid_rejected(self):
        from sales.services import add_job_payment

        job = self._closed_job()
        add_job_payment(
            job=job,
            user=self.lead,
            post={'pay_method': 'cash', 'pay_amount': '12', 'pay_date': date.today().isoformat()},
        )
        with self.assertRaisesMessage(ValueError, 'tahsilat'):
            adjust_closed_job(
                job=job,
                user=self.lead,
                post={'vat_mode': Job.VAT_NONE, 'grand_total': '10'},
            )
        job.refresh_from_db()
        self.assertEqual(job.grand_total, Decimal('15.00'))

    def test_adjust_saves_via_kaydet_post(self):
        job = self._closed_job()
        self.client.force_login(self.lead)
        page = self.client.get(job.get_absolute_url())
        self.assertContains(page, 'id="save-adjust"')
        self.assertContains(page, 'id="adjust-form"')
        self.assertContains(page, 'type="submit"')
        self.assertContains(page, 'formaction="')
        self.assertContains(page, 'action="'+job.get_absolute_url()+'"')
        response = self.client.post(
            job.get_absolute_url(),
            {'action': 'adjust', 'vat_mode': Job.VAT_PLUS, 'grand_total': '10'},
        )
        self.assertEqual(response.status_code, 302)
        job.refresh_from_db()
        self.assertEqual(job.status, Job.STATUS_CLOSED)
        self.assertIsNone(job.sale_id)
        self.assertEqual(job.vat_mode, Job.VAT_PLUS)
        self.assertEqual(job.grand_total, Decimal('10.00'))
        self.assertEqual(job.list_grand, Decimal('18.00'))
        self.assertEqual(job.discount_rate, Decimal('44.4444'))
        self.assertEqual(job.remaining, Decimal('10.00'))

    def test_field_tech_does_not_see_payment_details(self):
        job = self._closed_job()
        self.client.force_login(self.tech)
        office = self.client.get(job.get_absolute_url())
        self.assertEqual(office.status_code, 302)
        page = self.client.get(job.get_field_url())
        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, 'Ödeme detayları')
        self.assertNotContains(page, 'name="vat_mode"')
        self.client.post(
            job.get_absolute_url(),
            {'action': 'adjust', 'vat_mode': Job.VAT_PLUS, 'grand_total': '10'},
        )
        self.client.post(
            job.get_field_url(),
            {'action': 'adjust', 'vat_mode': Job.VAT_PLUS, 'grand_total': '10'},
        )
        job.refresh_from_db()
        self.assertEqual(job.grand_total, Decimal('15.00'))
        self.assertEqual(job.vat_mode, Job.VAT_NONE)


class SaleMountJobTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='mount-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.tech = Customer.objects.create_user(
            username='mount-tech',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        self.member = CrewMember.objects.create(
            number='CRWMNT1',
            first_name='Saha',
            last_name='Montaj',
            phone='05551112233',
            user=self.tech,
            created_by=self.lead,
        )
        self.party = Party.objects.create(
            kind=Party.KIND_REAL,
            number='CUSTC9001',
            first_name='Ayşe',
            last_name='Montaj',
            phone='05550001122',
            address='Test mah',
            created_by=self.lead,
        )
        self.category = Category.objects.create(
            name='Klima Split',
            slug='klima-split-test',
            sku_prefix='KS',
            is_klima=True,
            created_by=self.lead,
        )
        self.split = Product.objects.create(
            sku='KSSPL1',
            brand='Daikin',
            name='FTXM25',
            category=self.category,
            is_device=True,
            device_kind=Product.KIND_SPLIT,
            outdoor_name='RXM25',
            created_by=self.lead,
        )
        cat = Category.objects.create(
            name='Klima Servis',
            slug='klima-servis',
            sku_prefix='SV',
            created_by=self.lead,
        )
        self.labor = Product.objects.create(
            sku=SERVICE_LABOR_SKU,
            name='Demontaj - Montaj',
            category=cat,
            unit='AD',
            vat_rate=Decimal('20.00'),
            sale_price=Decimal('1500.00'),
            created_by=self.lead,
        )

    def _sale(self, number='SAL20990001', qty='2'):
        sale = Sale.objects.create(
            number=number,
            date=date.today(),
            party=self.party,
            work_type=Sale.WORK_DEVICE,
            vat_mode=Sale.VAT_PLUS,
            created_by=self.lead,
            updated_by=self.lead,
        )
        zero = Decimal('0.00')
        SaleLine.objects.create(
            sale=sale,
            product=self.split,
            qty=Decimal(qty),
            unit_price=zero,
            cost_price=zero,
            vat_rate=Decimal('20.00'),
            line_net=zero,
            line_vat=zero,
            line_total=zero,
        )
        return sale

    def _organic_post(self, **extra):
        data = {
            'action': 'save',
            'party_mode': 'existing',
            'party_id': str(self.party.pk),
            'date': date.today().isoformat(),
            'assignee_id': str(self.member.pk),
            'device_mode': 'none',
            'notes': 'Bakım',
        }
        data.update(extra)
        return data

    def test_schedule_sale_job_uses_sale_number_not_srv(self):
        sale = self._sale()
        job = schedule_sale_job(sale=sale, when=date.today(), user=self.lead, clock=time(10, 0))
        self.assertEqual(job.number, sale.number)
        self.assertTrue(job.number.startswith('SAL'))
        self.assertFalse(job.number.startswith('SRV'))
        self.assertEqual(job.status, Job.STATUS_PENDING)
        self.assertEqual(job.sale_id, sale.pk)
        self.assertEqual(Job.objects.filter(number__startswith='SRV').count(), 0)

    def test_sal_job_detail_url_accepts_lowercase_path(self):
        sale = self._sale()
        job = schedule_sale_job(sale=sale, when=date.today(), user=self.lead, clock=time(10, 0))
        url = reverse('portal-service-job-detail', kwargs={'number': job.number})
        self.assertEqual(url, '/service/jobs/sal20990001/')
        field_url = reverse('portal-field-job', kwargs={'number': job.number})
        self.assertEqual(field_url, '/field/jobs/sal20990001/')
        self.client.force_login(self.lead)
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Depodan alınacak')

    def test_job_list_kind_filter_and_organic_srv(self):
        sale = self._sale()
        mount = schedule_sale_job(sale=sale, when=date.today(), user=self.lead, clock=time(10, 0))
        organic = save_job(user=self.lead, post=self._organic_post())
        self.assertTrue(organic.number.startswith(f'SRV{date.today().year}'))
        self.assertRegex(organic.number, r'^SRV\d{8,}$')
        self.assertIsNone(organic.sale_id)
        self.client.force_login(self.lead)
        mount_page = self.client.get(reverse('portal-service-jobs'), {'kind': 'mount'})
        self.assertEqual(mount_page.status_code, 200)
        mount_jobs = list(mount_page.context['jobs'])
        self.assertEqual([item.pk for item in mount_jobs], [mount.pk])
        self.assertEqual(mount_jobs[0].kind_label, 'Montaj')
        self.assertEqual(mount_jobs[0].display_number, sale.number)
        self.assertContains(mount_page, sale.number)
        self.assertNotContains(mount_page, organic.number)
        service_page = self.client.get(reverse('portal-service-jobs'), {'kind': 'service'})
        service_jobs = list(service_page.context['jobs'])
        self.assertEqual([item.pk for item in service_jobs], [organic.pk])
        self.assertEqual(service_jobs[0].kind_label, 'Servis')
        self.assertNotContains(service_page, sale.number)

    def test_pending_mount_has_warehouse_list_not_device_picker(self):
        sale = self._sale(qty='1')
        job = schedule_sale_job(sale=sale, when=date.today(), user=self.lead, clock=time(10, 0))
        self.client.force_login(self.lead)
        page = self.client.get(job.get_absolute_url())
        body = page.content.decode()
        self.assertEqual(page.status_code, 200)
        self.assertIn('Depodan alınacak', body)
        self.assertIn('Daikin', body)
        self.assertIn('name="action"', body)
        self.assertNotIn('name="device_id"', body)
        self.assertNotIn('name="device_mode"', body)
        self.assertNotIn('Kayıtlı cihaz varsa seçin', body)
        self.assertEqual(page.context['assignee_id'], 'all')
        self.assertEqual(page.context['assignee_name'], 'Hepsi')
        self.assertIn('data-pick-id="all"', body)
        confirmed = confirm_job(
            job=job,
            user=self.lead,
            when=date.today(),
            clock=time(10, 0),
            assignee=self.member,
        )
        self.assertEqual(confirmed.status, Job.STATUS_OPEN)
        self.assertIsNone(confirmed.device_id)
        self.client.force_login(self.tech)
        field = self.client.get(confirmed.get_field_url())
        self.assertEqual(field.status_code, 200)
        self.assertNotContains(field, 'name="job_photos"')
        self.assertContains(field, 'unit_photos_')
        self.assertContains(field, 'data-pack-photos')

    def test_pending_confirm_assign_all(self):
        sale = self._sale(number='SAL20990050', qty='1')
        job = schedule_sale_job(sale=sale, when=date.today(), user=self.lead, clock=time(10, 0))
        confirmed = confirm_job(
            job=job,
            user=self.lead,
            when=date.today(),
            clock=time(10, 0),
            assign_all=True,
        )
        self.assertEqual(confirmed.status, Job.STATUS_OPEN)
        self.assertTrue(confirmed.assign_all)
        self.assertIsNone(confirmed.assignee_id)
        self.client.force_login(self.tech)
        field = self.client.get(confirmed.get_field_url())
        self.assertEqual(field.status_code, 200)
        self.assertTrue(field.context['can_edit'])

    def test_field_pack_photo_upload_appends(self):
        sale = self._sale(qty='1')
        job = schedule_sale_job(sale=sale, when=date.today(), user=self.lead, clock=time(10, 0))
        confirm_job(job=job, user=self.lead, when=date.today(), clock=time(10, 0), assignee=self.member)
        pack = job.sold_packs.first()
        png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00'
            b'\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
            b'\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        self.client.force_login(self.tech)

        def post_shot(name):
            upload = SimpleUploadedFile(name, png, content_type='image/png')
            return self.client.post(
                job.get_field_url(),
                {
                    'action': 'unit_photo',
                    'pack_id': str(pack.pk),
                    f'unit_photos_{pack.pk}': upload,
                },
                HTTP_ACCEPT='application/json',
            )

        first = post_shot('a.png')
        self.assertEqual(first.status_code, 200)
        data = first.json()
        self.assertTrue(data['ok'])
        self.assertEqual(len(data['photos']), 1)
        self.assertIn(f'group={pack.pk}', data['photos'][0]['url'])
        second = post_shot('b.png')
        self.assertEqual(second.status_code, 200)
        self.assertEqual(len(second.json()['photos']), 1)
        self.assertEqual(JobSoldUnitPhoto.objects.filter(pack=pack).count(), 2)
        shot = JobSoldUnitPhoto.objects.filter(pack=pack).order_by('id').first()
        image = self.client.get(job.get_field_url(), {'group': pack.pk, 'photo': shot.pk})
        self.assertEqual(image.status_code, 200)
        self.assertTrue(image.get('Content-Type', '').startswith('image/') or image.get('Content-Type') == 'application/octet-stream')
        gone = self.client.post(
            job.get_field_url(),
            {'action': 'delete_unit_photo', 'photo_id': str(shot.pk)},
            HTTP_ACCEPT='application/json',
        )
        self.assertEqual(gone.status_code, 200)
        self.assertTrue(gone.json()['ok'])
        self.assertEqual(JobSoldUnitPhoto.objects.filter(pack=pack).count(), 1)

    def test_organic_pending_keeps_device_on_confirm(self):
        device = Device.objects.create(
            party=self.party,
            name='ESKİ KLİMA',
            place='SALON',
            interval_months=6,
            created_by=self.lead,
        )
        job = Job.objects.create(
            number='SRV20991111',
            date=date.today() - timedelta(days=1),
            party=self.party,
            device=device,
            status=Job.STATUS_PENDING,
            created_by=self.lead,
            updated_by=self.lead,
        )
        self.client.force_login(self.lead)
        page = self.client.get(job.get_absolute_url())
        self.assertContains(page, 'ESKİ KLİMA')
        self.assertNotContains(page, 'Depodan alınacak')
        confirmed = confirm_job(
            job=job,
            user=self.lead,
            when=date.today(),
            clock=time(11, 0),
            assignee=self.member,
        )
        self.assertEqual(confirmed.device_id, device.pk)

    def test_close_sale_job_creates_one_device_per_pack(self):
        sale = self._sale(qty='2')
        job = schedule_sale_job(sale=sale, when=date.today(), user=self.lead, clock=time(10, 0))
        confirm_job(job=job, user=self.lead, when=date.today(), clock=time(10, 0), assignee=self.member)
        packs = list(job.sold_packs.order_by('sort', 'id'))
        units = list(job.sold_units.order_by('id'))
        self.assertEqual(len(packs), 2)
        self.assertEqual(len(units), 2)
        packs[0].interval_months = 9
        packs[0].outdoor_serial = 'OUT-1'
        packs[0].save(update_fields=['interval_months', 'outdoor_serial'])
        packs[1].outdoor_serial = 'OUT-2'
        packs[1].save(update_fields=['outdoor_serial'])
        units[0].room = 'salon'
        units[0].serial = 'IN-A'
        units[0].save(update_fields=['room', 'serial'])
        units[1].room = 'mutfak'
        units[1].serial = 'IN-B'
        units[1].save(update_fields=['room', 'serial'])
        job.status = Job.STATUS_SUBMITTED
        job.save(update_fields=['status'])
        with self.assertRaisesMessage(ValueError, 'Kapatma ofiste yapılır.'):
            close_job(job=job, user=self.tech)
        closed = close_job(job=job, user=self.lead)
        devices = list(Device.objects.filter(party=self.party).order_by('id'))
        self.assertEqual(len(devices), 2)
        self.assertEqual(closed.status, Job.STATUS_CLOSED)
        self.assertEqual(closed.device_id, devices[0].pk)
        self.assertEqual(devices[0].place, 'SALON')
        self.assertEqual(devices[0].interval_months, 9)
        self.assertEqual(devices[0].last_serviced_on, job.date)
        self.assertIn('OUT-1', devices[0].name)
        units[0].refresh_from_db()
        units[1].refresh_from_db()
        self.assertEqual(units[0].serial, 'IN-A')
        self.assertEqual(units[1].serial, 'IN-B')
        self.assertEqual(Device.objects.filter(name__icontains='IN-A').count(), 0)
        sale.refresh_from_db()
        self.assertFalse(any(field.name == 'status' for field in Sale._meta.fields))
        self.assertEqual(sale.invoice_status, Sale.INVOICE_NO)

    def test_organic_close_does_not_mint_pack_devices(self):
        job = save_job(user=self.lead, post=self._organic_post(work_id=str(self.labor.pk)))
        job.status = Job.STATUS_SUBMITTED
        job.save(update_fields=['status'])
        before = Device.objects.filter(party=self.party).count()
        closed = close_job(job=job, user=self.lead)
        self.assertEqual(closed.status, Job.STATUS_CLOSED)
        self.assertIsNone(closed.sale_id)
        self.assertEqual(Device.objects.filter(party=self.party).count(), before)
        self.assertEqual(closed.sold_packs.count(), 0)

    def test_relabel_mount_job_moves_srv_to_sale_number(self):
        sale = self._sale(number='SAL20990077')
        job = Job.objects.create(
            number='SRV20990077',
            date=date.today(),
            party=self.party,
            sale=sale,
            status=Job.STATUS_PENDING,
            created_by=self.lead,
            updated_by=self.lead,
        )
        relabel_mount_job(job)
        job.refresh_from_db()
        self.assertEqual(job.number, 'SAL20990077')
        other_sale = self._sale(number='SAL20990078')
        clash = Job.objects.create(
            number='SAL20990078',
            date=date.today(),
            party=self.party,
            status=Job.STATUS_OPEN,
            assignee=self.member,
            created_by=self.lead,
            updated_by=self.lead,
        )
        stuck = Job.objects.create(
            number='SRV20990078',
            date=date.today(),
            party=self.party,
            sale=other_sale,
            status=Job.STATUS_PENDING,
            created_by=self.lead,
            updated_by=self.lead,
        )
        relabel_mount_job(stuck)
        stuck.refresh_from_db()
        self.assertEqual(stuck.number, 'SRV20990078')
        self.assertEqual(clash.number, 'SAL20990078')

    def test_delete_sale_removes_mount_job(self):
        sale = self._sale(number='SAL20990101')
        job = schedule_sale_job(sale=sale, when=date.today(), user=self.lead, clock=time(10, 0))
        job_pk = job.pk
        sale_pk = sale.pk
        delete_sale(sale=sale, user=self.lead)
        self.assertFalse(Job.objects.filter(pk=job_pk).exists())
        self.assertFalse(Sale.objects.filter(pk=sale_pk).exists())

    def test_next_sale_number_skips_orphan_job(self):
        when = date.today()
        taken = f'SAL{when.year}0002'
        Job.objects.create(
            number=taken,
            date=when,
            party=self.party,
            status=Job.STATUS_OPEN,
            assignee=self.member,
            created_by=self.lead,
            updated_by=self.lead,
        )
        nxt = next_sale_number(when)
        self.assertNotEqual(nxt, taken)
        self.assertGreater(int(nxt[len(f'SAL{when.year}'):]), 2)

    def test_field_mount_save_opens_summary_without_submit(self):
        png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00'
            b'\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
            b'\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        sale = self._sale(qty='1')
        job = schedule_sale_job(sale=sale, when=date.today(), user=self.lead, clock=time(10, 0))
        confirm_job(job=job, user=self.lead, when=date.today(), clock=time(10, 0), assignee=self.member)
        pack = job.sold_packs.get()
        unit = job.sold_units.get()
        mount = Category.objects.create(
            name='Klima Montaj Malzemesi',
            slug=MOUNT_CATEGORY_SLUG,
            sku_prefix=MOUNT_SKU_PREFIX,
            created_by=self.lead,
        )
        self.tech.stock_categories.add(mount)
        pipe = Product.objects.create(
            sku='KMM-0100',
            name='Bakır Boru',
            category=mount,
            unit='MT',
            stock_qty=Decimal('20.00'),
            created_by=self.lead,
        )
        for index in range(4):
            JobSoldUnitPhoto.objects.create(
                pack=pack,
                image=SimpleUploadedFile(f'{index}.png', png, content_type='image/png'),
                sort=index,
            )
        self.client.force_login(self.tech)
        form_page = self.client.get(job.get_field_url())
        self.assertEqual(form_page.status_code, 200)
        self.assertContains(form_page, 'Kaydet')
        self.assertContains(form_page, 'Bakım')
        self.assertContains(form_page, f'pack_interval_{pack.pk}')
        self.assertNotContains(form_page, 'Yazdır')
        blocked = self.client.get(job.get_field_url(), {'summary': '1'})
        self.assertEqual(blocked.status_code, 302)
        self.assertEqual(blocked.url, job.get_field_url())
        saved = self.client.post(
            job.get_field_url(),
            {
                'action': 'save',
                f'unit_room_{unit.pk}': 'salon',
                f'unit_serial_{unit.pk}': 'in-1',
                f'pack_outdoor_serial_{pack.pk}': 'out-1',
                f'pack_interval_{pack.pk}': '9',
                f'pack_last_{pack.pk}': job.date.isoformat(),
                'field_mat_present': '1',
                'field_mat_product': str(pipe.pk),
                'field_mat_qty': '2',
            },
        )
        self.assertRedirects(saved, f'{job.get_field_url()}?summary=1')
        job.refresh_from_db()
        self.assertEqual(job.status, Job.STATUS_OPEN)
        page = self.client.get(job.get_field_url(), {'summary': '1'})
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Montaj fişi')
        self.assertContains(page, 'SALON')
        self.assertContains(page, 'İN-1')
        self.assertContains(page, 'OUT-1')
        self.assertContains(page, 'Bakır Boru')
        self.assertContains(page, '9 ay')
        pack.refresh_from_db()
        self.assertEqual(pack.interval_months, 9)
        self.assertEqual(pack.last_serviced_on, job.date)
        self.assertIsNotNone(pack.next_due)
        self.assertContains(page, 'Tekrar düzenle')
        self.assertContains(page, 'Yazdır')
        self.assertContains(page, 'İşi tamamla')
        self.assertNotContains(page, 'Teslim et')
        self.assertNotContains(page, 'id="field-job-form"')
        again = self.client.post(
            job.get_field_url(),
            {
                'action': 'save',
                f'unit_room_{unit.pk}': 'salon',
                f'unit_serial_{unit.pk}': 'in-1',
                f'pack_outdoor_serial_{pack.pk}': 'out-1',
                f'pack_interval_{pack.pk}': '9',
                f'pack_last_{pack.pk}': job.date.isoformat(),
                'field_mat_present': '1',
                'field_mat_product': str(pipe.pk),
                'field_mat_qty': '2',
            },
        )
        self.assertRedirects(again, f'{job.get_field_url()}?summary=1')
        pipe.refresh_from_db()
        self.assertEqual(pipe.stock_qty, Decimal('18.00'))
        self.assertEqual(StockMovement.objects.filter(job=job, product=pipe).count(), 1)
        json_saved = self.client.post(
            job.get_field_url(),
            {
                'action': 'save',
                f'unit_room_{unit.pk}': 'salon',
                f'unit_serial_{unit.pk}': 'in-1',
                f'pack_outdoor_serial_{pack.pk}': 'out-1',
                f'pack_interval_{pack.pk}': '9',
                f'pack_last_{pack.pk}': job.date.isoformat(),
                'field_mat_present': '1',
                'field_mat_product': str(pipe.pk),
                'field_mat_qty': '2',
            },
            HTTP_ACCEPT='application/json',
        )
        self.assertEqual(json_saved.status_code, 200)
        self.assertTrue(json_saved.json()['ok'])
        self.assertEqual(json_saved.json()['next'], f'{job.get_field_url()}?summary=1')
        pipe.refresh_from_db()
        self.assertEqual(pipe.stock_qty, Decimal('18.00'))
        office = self.client
        office.force_login(self.lead)
        desk = office.get(job.get_absolute_url())
        self.assertEqual(desk.status_code, 200)
        self.assertNotContains(desk, 'Montaj fişi')
        self.client.force_login(self.tech)
        handed = self.client.post(job.get_field_url(), {'action': 'submit'})
        self.assertRedirects(handed, reverse('portal-field'))
        job.refresh_from_db()
        self.assertEqual(job.status, Job.STATUS_SUBMITTED)
        home = self.client.get(reverse('portal-field'))
        self.assertContains(home, 'Son tamamlanan')
        self.assertContains(home, job.number)
        done = self.client.get(job.get_field_url())
        self.assertContains(done, 'Montaj fişi')
        self.assertContains(done, 'Teslim edildi')
        self.assertContains(done, 'Yazdır')
        self.assertNotContains(done, 'Teslim et')
        self.assertNotContains(done, 'İşi tamamla')
        self.assertNotContains(done, 'Tekrar düzenle')

    def test_office_closes_mount_without_registered_device(self):
        sale = self._sale(qty='1')
        job = schedule_sale_job(sale=sale, when=date.today(), user=self.lead, clock=time(10, 0))
        confirm_job(job=job, user=self.lead, when=date.today(), clock=time(10, 0), assignee=self.member)
        pack = job.sold_packs.get()
        unit = job.sold_units.get()
        unit.room = 'SALON'
        unit.serial = 'IN-1'
        unit.save(update_fields=['room', 'serial'])
        pack.outdoor_serial = 'OUT-1'
        pack.interval_months = 9
        pack.last_serviced_on = job.date
        pack.save(update_fields=['outdoor_serial', 'interval_months', 'last_serviced_on'])
        job.status = Job.STATUS_SUBMITTED
        job.save(update_fields=['status'])
        self.assertIsNone(job.device_id)
        self.client.force_login(self.lead)
        page = self.client.get(job.get_absolute_url())
        self.assertContains(page, 'Kapat')
        self.assertContains(page, 'name="device_mode"')
        self.assertNotContains(page, 'id="job-error">Kayıtlı cihaz seçin.')
        closed = self.client.post(
            job.get_absolute_url(),
            {
                'action': 'close',
                'party_mode': 'existing',
                'party_id': str(self.party.pk),
                'assignee_id': str(self.member.pk),
                'date': job.date.isoformat(),
                'device_mode': 'existing',
                'device_id': '',
            },
        )
        self.assertRedirects(closed, job.get_absolute_url())
        job.refresh_from_db()
        unit.refresh_from_db()
        pack.refresh_from_db()
        self.assertEqual(job.status, Job.STATUS_CLOSED)
        self.assertIsNotNone(job.device_id)
        self.assertEqual(unit.room, 'SALON')
        self.assertEqual(unit.serial, 'IN-1')
        self.assertEqual(pack.outdoor_serial, 'OUT-1')
        self.assertEqual(Device.objects.filter(party=self.party).count(), 1)

    def test_legal_mount_visible_on_service_field_and_device_place(self):
        legal = Party.objects.create(
            kind=Party.KIND_LEGAL,
            number='CUSTC9010',
            company_name='Beztas Montaj',
            first_name='Ali',
            last_name='Yetkili',
            tax_no='1234567890',
            phone='05550001122',
            address='Fatura mah',
            city='BURSA',
            district='OSMANGAZİ',
            created_by=self.lead,
        )
        sale = self._sale(number='SAL20990110', qty='1')
        sale.party = legal
        sale.mount_contact_name = 'ŞANTİYE AHMET'
        sale.mount_phone = '0 (555) 111 22 33'
        sale.mount_city = 'BURSA'
        sale.mount_district = 'NİLÜFER'
        sale.mount_address = 'ŞANTİYE KAPI 2'
        sale.mount_notes = 'Akşam gelin'
        sale.save(
            update_fields=[
                'party',
                'mount_contact_name',
                'mount_phone',
                'mount_city',
                'mount_district',
                'mount_address',
                'mount_notes',
            ]
        )
        job = schedule_sale_job(sale=sale, when=date.today(), user=self.lead, clock=time(10, 0))
        self.client.force_login(self.lead)
        pending = self.client.get(job.get_absolute_url())
        self.assertContains(pending, 'Montaj yeri')
        self.assertContains(pending, 'ŞANTİYE AHMET')
        self.assertContains(pending, 'ŞANTİYE KAPI 2')
        self.assertContains(pending, 'Akşam gelin')
        confirm_job(job=job, user=self.lead, when=date.today(), clock=time(10, 0), assignee=self.member)
        self.client.force_login(self.tech)
        field = self.client.get(job.get_field_url())
        self.assertContains(field, 'Montaj yeri')
        self.assertContains(field, 'ŞANTİYE AHMET')
        self.assertContains(field, 'Akşam gelin')
        pack = job.sold_packs.get()
        unit = job.sold_units.get()
        unit.room = 'SALON'
        unit.serial = 'IN-MT-1'
        unit.save(update_fields=['room', 'serial'])
        pack.outdoor_serial = 'OUT-MT-1'
        pack.interval_months = 6
        pack.last_serviced_on = job.date
        pack.save(update_fields=['outdoor_serial', 'interval_months', 'last_serviced_on'])
        job.status = Job.STATUS_SUBMITTED
        job.save(update_fields=['status'])
        closed = close_job(job=job, user=self.lead)
        device = closed.device
        self.assertIsNotNone(device)
        self.assertIn('NİLÜFER / BURSA', device.place)
        self.assertIn('ŞANTİYE KAPI 2', device.place)
        self.client.force_login(self.lead)
        customer = self.client.get(legal.get_absolute_url() + '?tab=devices')
        self.assertContains(customer, 'NİLÜFER / BURSA')
        self.assertContains(customer, 'ŞANTİYE KAPI 2')
        self.assertContains(customer, 'ŞANTİYE AHMET')
        self.assertIn('NİLÜFER / BURSA', device.place)
        self.assertIn('ŞANTİYE KAPI 2', device.place)


class MountActivationBackfillTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='act-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.party = Party.objects.create(
            kind=Party.KIND_REAL,
            number='CUSTC8111',
            first_name='Ali',
            last_name='Aktif',
            phone='05550001122',
            address='Test',
            city='BURSA',
            district='NİLÜFER',
            created_by=self.lead,
        )
        self.category = Category.objects.create(
            name='Klima Split Act',
            slug='klima-split-act',
            sku_prefix='KA',
            is_klima=True,
            created_by=self.lead,
        )
        self.split = Product.objects.create(
            sku='KASPL1',
            brand='Daikin',
            name='FTXM25',
            category=self.category,
            is_device=True,
            device_kind=Product.KIND_SPLIT,
            outdoor_name='RXM25',
            stock_qty=Decimal('5.00'),
            created_by=self.lead,
        )

    def _past_sale(self):
        when = date.today() - timedelta(days=40)
        sale = Sale.objects.create(
            number='SAL20998801',
            date=when,
            party=self.party,
            work_type=Sale.WORK_DEVICE,
            vat_mode=Sale.VAT_NONE,
            subtotal=Decimal('1000.00'),
            vat_total=Decimal('0.00'),
            grand_total=Decimal('1000.00'),
            created_by=self.lead,
            updated_by=self.lead,
        )
        zero = Decimal('0.00')
        SaleLine.objects.create(
            sale=sale,
            product=self.split,
            qty=Decimal('1'),
            unit_price=Decimal('1000.00'),
            cost_price=zero,
            vat_rate=zero,
            line_net=Decimal('1000.00'),
            line_vat=zero,
            line_total=Decimal('1000.00'),
        )
        return sale

    def test_activate_past_sale_creates_closed_device(self):
        sale = self._past_sale()
        rows = sale_mount_preview_rows(sale)
        self.assertEqual(len(rows), 1)
        key = rows[0]['source_key']
        post = {
            'interval_months': '9',
            f'serial_{key}': 'in-past-1',
            f'outdoor_{key}': 'out-past-1',
        }
        job = activate_sale_mount(sale=sale, user=self.lead, post=post)
        self.assertEqual(job.status, Job.STATUS_CLOSED)
        self.assertEqual(job.date, sale.date)
        self.assertIsNotNone(job.device_id)
        pack = job.sold_packs.get()
        self.assertEqual(pack.outdoor_serial, 'OUT-PAST-1')
        self.assertEqual(pack.interval_months, 9)
        self.assertEqual(pack.last_serviced_on, sale.date)
        unit = pack.units.get()
        self.assertEqual(unit.serial, 'İN-PAST-1')
        device = job.device
        self.assertEqual(device.last_serviced_on, sale.date)
        self.assertEqual(device.interval_months, 9)
        from service.services import add_months

        self.assertEqual(device.next_due, add_months(sale.date, 9))

    def test_activate_twice_rejected(self):
        sale = self._past_sale()
        rows = sale_mount_preview_rows(sale)
        key = rows[0]['source_key']
        post = {
            'interval_months': '6',
            f'serial_{key}': 'in-1',
            f'outdoor_{key}': 'out-1',
        }
        activate_sale_mount(sale=sale, user=self.lead, post=post)
        with self.assertRaisesMessage(ValueError, 'Bu satış zaten aktif edilmiş.'):
            activate_sale_mount(sale=sale, user=self.lead, post=post)

    def test_mount_activation_page_lists_past_sale(self):
        sale = self._past_sale()
        self.client.force_login(self.lead)
        page = self.client.get('/sales/mount-activation/')
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, sale.number)
        self.assertContains(page, 'Bakım aralığı')
        self.assertContains(page, 'value="12" checked')


class CopperMountSummaryTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='copper-sum-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.member = CrewMember.objects.create(
            number='CRWCU1',
            first_name='Saha',
            last_name='Bakır',
            phone='05551113344',
            created_by=self.lead,
        )
        self.party = Party.objects.create(
            kind=Party.KIND_REAL,
            number='CUSTCU100',
            first_name='Ravil',
            last_name='Test',
            phone='05550006677',
            address='Test',
            created_by=self.lead,
        )
        self.klima = Category.objects.create(
            name='Mitsubishi Copper',
            slug='mitsubishi-copper',
            sku_prefix='MHC',
            is_klima=True,
            included_copper_meters=Decimal('5.00'),
            created_by=self.lead,
        )
        self.copper_cat, _ = Category.objects.get_or_create(
            slug='bakir-boru-test',
            defaults={
                'name': 'Bakır Boru Test',
                'sku_prefix': 'BBT',
                'is_copper_pipe': True,
                'created_by': self.lead,
            },
        )
        if not self.copper_cat.is_copper_pipe:
            self.copper_cat.is_copper_pipe = True
            self.copper_cat.save(update_fields=['is_copper_pipe'])
        self.mount, _ = Category.objects.get_or_create(
            slug=MOUNT_CATEGORY_SLUG,
            defaults={
                'name': 'Klima Montaj Malzemesi',
                'sku_prefix': MOUNT_SKU_PREFIX,
                'created_by': self.lead,
            },
        )
        self.split = Product.objects.create(
            sku='MHC-0001',
            brand='Mitsubishi',
            name='Split',
            category=self.klima,
            is_device=True,
            device_kind=Product.KIND_SPLIT,
            outdoor_name='Outdoor',
            created_by=self.lead,
        )
        self.pipe = Product.objects.create(
            sku='BBT-0001',
            brand='Anadolu',
            name='1/4-1/2 Bakır Boru',
            category=self.copper_cat,
            unit='MT',
            stock_qty=Decimal('100.00'),
            sale_price=Decimal('40.00'),
            created_by=self.lead,
        )
        self.foot = Product.objects.create(
            sku=f'{MOUNT_SKU_PREFIX}-0098',
            brand='Genel',
            name='Yer Takozu',
            category=self.mount,
            unit='ADET',
            stock_qty=Decimal('50.00'),
            created_by=self.lead,
        )
        zero = Decimal('0.00')
        self.sale = Sale.objects.create(
            number='SALCU0001',
            date=date.today(),
            party=self.party,
            work_type=Sale.WORK_DEVICE,
            vat_mode=Sale.VAT_NONE,
            grand_total=zero,
            created_by=self.lead,
            updated_by=self.lead,
        )
        SaleLine.objects.create(
            sale=self.sale,
            product=self.split,
            qty=Decimal('1.00'),
            unit_price=zero,
            cost_price=zero,
            vat_rate=zero,
            line_net=zero,
            line_vat=zero,
            line_total=zero,
        )
        self.job = Job.objects.create(
            number='SRV20990101',
            date=date.today(),
            party=self.party,
            sale=self.sale,
            status=Job.STATUS_OPEN,
            assignee=self.member,
            created_by=self.lead,
            updated_by=self.lead,
        )
        ensure_sold_packs(self.job)

    def test_excess_without_agreed_copper(self):
        from service.services import copper_mount_summary

        pack = self.job.sold_packs.get()
        JobSoldUnitMaterial.objects.create(
            pack=pack,
            product=self.pipe,
            qty=Decimal('23.00'),
            name=self.pipe.name,
            unit_label='MT',
        )
        JobSoldUnitMaterial.objects.create(
            pack=pack,
            product=self.foot,
            qty=Decimal('4.00'),
            name=self.foot.name,
            unit_label='ADET',
        )
        summary = copper_mount_summary(self.job)
        self.assertIsNotNone(summary)
        self.assertEqual(summary['used'], Decimal('23.00'))
        self.assertEqual(summary['included'], Decimal('5.00'))
        self.assertEqual(summary['agreed'], Decimal('0.00'))
        self.assertEqual(summary['excess'], Decimal('18.00'))
        self.assertTrue(summary['has_excess'])

    def test_excess_cleared_by_sale_agreed_meters(self):
        from sales.services import COPPER_LINE_DESCRIPTION
        from service.services import copper_mount_summary

        zero = Decimal('0.00')
        SaleLine.objects.create(
            sale=self.sale,
            product=None,
            description=COPPER_LINE_DESCRIPTION,
            is_copper=True,
            qty=Decimal('18.00'),
            unit_price=Decimal('50.00'),
            cost_price=zero,
            vat_rate=zero,
            line_net=Decimal('900.00'),
            line_vat=zero,
            line_total=Decimal('900.00'),
        )
        pack = self.job.sold_packs.get()
        JobSoldUnitMaterial.objects.create(
            pack=pack,
            product=self.pipe,
            qty=Decimal('23.00'),
            name=self.pipe.name,
            unit_label='MT',
        )
        summary = copper_mount_summary(self.job)
        self.assertEqual(summary['excess'], Decimal('0.00'))
        self.assertFalse(summary['has_excess'])
        self.assertEqual(summary['agreed'], Decimal('18.00'))

    def test_multi_pack_adds_no_included_meters(self):
        from service.models import JobSoldPack
        from service.services import copper_mount_summary

        pack = self.job.sold_packs.get()
        pack.kind = JobSoldPack.KIND_MULTI
        pack.save(update_fields=['kind'])
        JobSoldUnitMaterial.objects.create(
            pack=pack,
            product=self.pipe,
            qty=Decimal('10.00'),
            name=self.pipe.name,
            unit_label='MT',
        )
        summary = copper_mount_summary(self.job)
        self.assertEqual(summary['included'], Decimal('0.00'))
        self.assertEqual(summary['excess'], Decimal('10.00'))

    def test_field_mount_search_includes_copper_category(self):
        field = Customer.objects.create_user(
            username='copper-field',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        member = CrewMember.objects.create(
            number='CRWCU2',
            first_name='Field',
            last_name='Cu',
            phone='05551114455',
            user=field,
            created_by=self.lead,
        )
        field.stock_categories.add(self.mount, self.copper_cat)
        self.job.assignee = member
        self.job.save(update_fields=['assignee'])
        self.client.force_login(field)
        products = self.client.get(reverse('portal-field-products'), {'mount': '1'})
        self.assertEqual(products.status_code, 200)
        skus = {item['sku'] for item in products.json()['results']}
        self.assertIn('BBT-0001', skus)
        self.assertIn(f'{MOUNT_SKU_PREFIX}-0098', skus)
        page = self.client.get(reverse('portal-field-job', kwargs={'number': self.job.number}))
        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, 'data-copper-excess')

    def test_field_mount_access_covers_copper_without_explicit_grant(self):
        field = Customer.objects.create_user(
            username='copper-field-mount-only',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        field.stock_categories.add(self.mount)
        self.client.force_login(field)
        products = self.client.get(reverse('portal-field-products'), {'mount': '1'})
        skus = {item['sku'] for item in products.json()['results']}
        self.assertIn('BBT-0001', skus)
        nobody = Customer.objects.create_user(
            username='copper-field-none',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        self.client.force_login(nobody)
        products = self.client.get(reverse('portal-field-products'), {'mount': '1'})
        self.assertNotIn('BBT-0001', {item['sku'] for item in products.json()['results']})

    def test_copper_material_moves_stock_and_returns(self):
        from service.services import _set_pack_materials, _sync_mount_stock

        pack = self.job.sold_packs.get()
        _set_pack_materials(pack, {self.pipe.pk: Decimal('7.50')}, user=self.lead)
        _sync_mount_stock(job=self.job, user=self.lead)
        self.pipe.refresh_from_db()
        self.assertEqual(self.pipe.stock_qty, Decimal('92.50'))
        _sync_mount_stock(job=self.job, user=self.lead, wanted={})
        self.pipe.refresh_from_db()
        self.assertEqual(self.pipe.stock_qty, Decimal('100.00'))

    def test_excess_estimate_uses_agreed_price(self):
        from service.services import copper_mount_summary

        zero = Decimal('0.00')
        SaleLine.objects.create(
            sale=self.sale,
            product=self.pipe,
            description='Bakır boru',
            is_copper=True,
            qty=Decimal('3.00'),
            unit_price=Decimal('60.00'),
            cost_price=zero,
            vat_rate=zero,
            line_net=Decimal('180.00'),
            line_vat=zero,
            line_total=Decimal('180.00'),
        )
        JobSoldUnitMaterial.objects.create(
            pack=self.job.sold_packs.get(),
            product=self.pipe,
            qty=Decimal('10.00'),
            name=self.pipe.name,
            unit_label='MT',
        )
        summary = copper_mount_summary(self.job)
        self.assertEqual(summary['excess'], Decimal('2.00'))
        self.assertEqual(summary['excess_estimate'], Decimal('120.00'))
        self.assertFalse(summary['non_meter'])

    def test_field_qty_dot_is_decimal(self):
        from service.services import _parse_field_materials

        post = QueryDict(mutable=True)
        post.setlist('field_mat_product', [str(self.pipe.pk)])
        post.setlist('field_mat_qty', ['2.500'])
        self.assertEqual(_parse_field_materials(post), {self.pipe.pk: Decimal('2.50')})


class MaintenanceBellTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='bell-lead', password='pass-word', is_staff=True, role=Customer.ROLE_SERVICE_LEAD
        )
        self.sales = Customer.objects.create_user(
            username='bell-sales', password='pass-word', is_staff=True, role=Customer.ROLE_SALES
        )
        party = Party.objects.create(
            kind=Party.KIND_REAL, number='CUSTBELL1', first_name='Bell', last_name='Test',
            phone='05550009988', address='Test', created_by=self.lead,
        )
        today = timezone.localdate()
        for name, offset in (('Geciken', -3), ('Yakın', 5), ('Uzak', 40)):
            Device.objects.create(
                party=party, name=name, interval_months=6,
                next_due=today + timedelta(days=offset), created_by=self.lead,
            )

    def test_summary_counts_and_items(self):
        self.client.force_login(self.lead)
        data = self.client.get(reverse('portal-service-reminders-summary')).json()
        self.assertEqual((data['overdue'], data['soon'], data['total']), (1, 1, 2))
        self.assertEqual([item['device'] for item in data['items']], ['Geciken', 'Yakın'])
        self.assertTrue(data['items'][0]['overdue'])

    def test_summary_lead_only_and_bell_render(self):
        self.client.force_login(self.sales)
        self.assertNotEqual(self.client.get(reverse('portal-service-reminders-summary')).status_code, 200)
        page = self.client.get(reverse('portal-dashboard'))
        self.assertNotContains(page, 'class="bell"')
        self.assertNotContains(page, 'Bakımlar</a>')
        self.client.force_login(self.lead)
        page = self.client.get(reverse('portal-dashboard'))
        self.assertContains(page, 'class="bell"')
        self.assertContains(page, reverse('portal-service-reminders'))
