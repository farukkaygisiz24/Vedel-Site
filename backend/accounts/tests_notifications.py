import json
from datetime import time, timedelta
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.digest import field_digest, maintenance_heads_up
from accounts.models import Customer, Notification, PushSubscription
from accounts.notifications import notify, prune
from crew.models import CrewMember
from sales.models import Party
from service.models import Device, Job


class NotifyBase(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='n-lead', password='pass-word', is_staff=True, role=Customer.ROLE_SERVICE_LEAD
        )
        self.sales = Customer.objects.create_user(
            username='n-sales', password='pass-word', is_staff=True, role=Customer.ROLE_SALES
        )
        self.tech_user = Customer.objects.create_user(
            username='n-tech', password='pass-word', is_staff=True, role=Customer.ROLE_SERVICE
        )
        self.other_user = Customer.objects.create_user(
            username='n-tech2', password='pass-word', is_staff=True, role=Customer.ROLE_SERVICE
        )
        self.tech = CrewMember.objects.create(
            number='CRWN1', first_name='Selim', last_name='Saha', phone='05550000001',
            user=self.tech_user, created_by=self.lead,
        )
        self.other = CrewMember.objects.create(
            number='CRWN2', first_name='Enes', last_name='Saha', phone='05550000002',
            user=self.other_user, created_by=self.lead,
        )
        self.party = Party.objects.create(
            kind=Party.KIND_REAL, number='PN1', first_name='Ahmet', last_name='Yılmaz',
            phone='05550000003', created_by=self.lead,
        )
        self.today = timezone.localdate()

    def _job(self, number='SRV20990101', **kwargs):
        data = {
            'number': number,
            'date': self.today + timedelta(days=3),
            'time': time(10, 0),
            'party': self.party,
            'status': Job.STATUS_OPEN,
            'created_by': self.lead,
            'updated_by': self.lead,
        }
        data.update(kwargs)
        with self.captureOnCommitCallbacks(execute=True):
            return Job.objects.create(**data)

    def _save(self, job, **changes):
        for key, value in changes.items():
            setattr(job, key, value)
        with self.captureOnCommitCallbacks(execute=True):
            job.save()
        return job

    def kinds(self, user):
        return list(Notification.objects.filter(recipient=user).order_by('id').values_list('kind', flat=True))


class JobEventTests(NotifyBase):
    def test_assign_notifies_technician_with_relative_day(self):
        job = self._job(assignee=self.tech)
        note = Notification.objects.get(recipient=self.tech_user)
        self.assertEqual(note.kind, Notification.KIND_JOB_ASSIGNED)
        self.assertEqual(note.title, 'Yeni servis işi · Ahmet Yılmaz')
        self.assertTrue(note.body.endswith('10:00 (3 gün sonra)'))
        self.assertNotIn('Ahmet', note.body)
        self.assertEqual(note.url, job.get_field_url())
        self.assertEqual(self.kinds(self.other_user), [])

    def test_pending_job_is_not_sent_until_confirmed(self):
        job = self._job(assignee=self.tech, status=Job.STATUS_PENDING)
        self.assertEqual(self.kinds(self.tech_user), [])
        self._save(job, status=Job.STATUS_OPEN)
        self.assertEqual(self.kinds(self.tech_user), [Notification.KIND_JOB_ASSIGNED])

    def test_reschedule_and_reassign(self):
        job = self._job(assignee=self.tech)
        self._save(job, date=self.today + timedelta(days=5), time=time(14, 0))
        self.assertEqual(
            self.kinds(self.tech_user),
            [Notification.KIND_JOB_ASSIGNED, Notification.KIND_JOB_RESCHEDULED],
        )
        moved = Notification.objects.filter(recipient=self.tech_user).order_by('id').last()
        self.assertIn('→', moved.body)
        self._save(job, assignee=self.other)
        self.assertEqual(self.kinds(self.tech_user)[-1], Notification.KIND_JOB_UNASSIGNED)
        self.assertEqual(
            Notification.objects.filter(recipient=self.tech_user).order_by('id').last().title,
            'İş başkasına verildi · SRV20990101',
        )
        self.assertEqual(self.kinds(self.other_user), [Notification.KIND_JOB_ASSIGNED])

    def test_pool_job_reaches_every_technician(self):
        self._job(assign_all=True)
        self.assertEqual(self.kinds(self.tech_user), [Notification.KIND_JOB_ASSIGNED])
        self.assertEqual(self.kinds(self.other_user), [Notification.KIND_JOB_ASSIGNED])

    def test_delete_cancels(self):
        job = self._job(assignee=self.tech)
        with self.captureOnCommitCallbacks(execute=True):
            job.delete()
        self.assertEqual(self.kinds(self.tech_user)[-1], Notification.KIND_JOB_CANCELLED)

    def test_submit_reaches_leads_not_actor(self):
        job = self._job(assignee=self.tech)
        self._save(job, status=Job.STATUS_SUBMITTED, updated_by=self.tech_user)
        self.assertIn(Notification.KIND_JOB_SUBMITTED, self.kinds(self.lead))
        self.assertNotIn(Notification.KIND_JOB_UNASSIGNED, self.kinds(self.tech_user))

    def test_actor_never_notifies_self(self):
        self._job(assignee=self.tech, created_by=self.tech_user, updated_by=self.tech_user)
        self.assertEqual(self.kinds(self.tech_user), [])

    def test_organic_job_reaches_leads(self):
        self._job(created_by=self.sales, updated_by=self.sales)
        self.assertEqual(self.kinds(self.lead), [Notification.KIND_JOB_NEW])
        self.assertEqual(self.kinds(self.sales), [])

    def test_lead_with_crew_card_gets_one_notice_when_assigned(self):
        lead_member = CrewMember.objects.create(
            number='CRWN3', first_name='Lider', last_name='Saha', phone='05550000004',
            user=self.lead, created_by=self.sales,
        )
        self._job(assignee=lead_member, created_by=self.sales, updated_by=self.sales)
        self.assertEqual(self.kinds(self.lead), [Notification.KIND_JOB_ASSIGNED])


class NotificationViewTests(NotifyBase):
    def test_summary_read_and_page(self):
        notify([self.lead], kind=Notification.KIND_SALE_NEW, title='A', actor=self.sales, send_push=False)
        notify([self.lead], kind=Notification.KIND_SALE_NEW, title='B', actor=self.sales, send_push=False)
        self.client.force_login(self.lead)
        data = self.client.get(reverse('portal-notifications-summary')).json()
        self.assertEqual(data['unread'], 2)
        self.assertEqual([item['title'] for item in data['items']], ['B', 'A'])
        first = data['items'][1]['id']
        res = self.client.post(reverse('portal-notifications-read'), {'ids': str(first)}).json()
        self.assertEqual(res['unread'], 1)
        page = self.client.get(reverse('portal-notifications'), {'show': 'unread'})
        self.assertContains(page, 'B')
        self.assertNotContains(page, '<b>A</b>', html=False)
        res = self.client.post(reverse('portal-notifications-read'), {'ids': 'all'}).json()
        self.assertEqual(res['unread'], 0)

    def test_users_only_see_their_own(self):
        note = notify([self.sales], kind=Notification.KIND_SALE_NEW, title='Gizli', send_push=False)[0]
        self.client.force_login(self.lead)
        self.client.post(reverse('portal-notifications-read'), {'ids': str(note.pk)})
        note.refresh_from_db()
        self.assertIsNone(note.read_at)
        self.assertNotContains(self.client.get(reverse('portal-notifications')), 'Gizli')

    def test_field_user_has_no_notifications_page(self):
        self.client.force_login(self.tech_user)
        page = self.client.get(reverse('portal-notifications'))
        self.assertRedirects(page, reverse('portal-field'), fetch_redirect_response=False)
        home = self.client.get(reverse('portal-field'))
        self.assertContains(home, 'class="field-bell-pop"')
        self.assertNotContains(home, 'href="%s"' % reverse('portal-notifications'))

    def test_dedupe_and_prune(self):
        notify([self.lead], kind=Notification.KIND_DIGEST, title='x', dedupe_key='k1', send_push=False)
        notify([self.lead], kind=Notification.KIND_DIGEST, title='x', dedupe_key='k1', send_push=False)
        self.assertEqual(Notification.objects.filter(recipient=self.lead).count(), 1)
        Notification.objects.update(created_at=timezone.now() - timedelta(days=91))
        self.assertEqual(prune(), 1)


@override_settings(PUSH_ENABLED=True, VAPID_PRIVATE_KEY='x', VAPID_PUBLIC_KEY='y', PUSH_SYNC=True)
class PushTests(NotifyBase):
    def _sub(self, user, endpoint):
        return PushSubscription.objects.create(user=user, endpoint=endpoint, p256dh='p', auth='a')

    def test_subscribe_endpoint(self):
        self.client.force_login(self.tech_user)
        body = '{"endpoint": "https://push.example/abc", "keys": {"p256dh": "k", "auth": "s"}}'
        res = self.client.post(reverse('portal-push-subscription'), body, content_type='application/json')
        self.assertTrue(res.json()['ok'])
        self.assertEqual(PushSubscription.objects.get().user, self.tech_user)
        res = self.client.delete(reverse('portal-push-subscription'), body, content_type='application/json')
        self.assertFalse(PushSubscription.objects.exists())

    def test_assignment_pushes_and_drops_gone_subscriptions(self):
        from pywebpush import WebPushException

        keep = self._sub(self.tech_user, 'https://push.example/keep')
        self._sub(self.tech_user, 'https://push.example/gone')
        gone = mock.Mock(status_code=410)

        def fake(subscription_info, data, **kwargs):
            if subscription_info['endpoint'].endswith('gone'):
                raise WebPushException('gone', response=gone)

        with mock.patch('pywebpush.webpush', side_effect=fake) as sent:
            self._job(assignee=self.tech)
        self.assertEqual(sent.call_count, 2)
        payload = json.loads(sent.call_args_list[0].kwargs['data'])
        self.assertEqual(payload['title'], 'Yeni servis işi · Ahmet Yılmaz')
        self.assertEqual(payload['url'], '/field/jobs/srv20990101/')
        self.assertEqual(list(PushSubscription.objects.values_list('pk', flat=True)), [keep.pk])
        keep.refresh_from_db()
        self.assertIsNotNone(keep.last_ok_at)


class DigestTests(NotifyBase):
    def test_field_digest_counts_tomorrow_once(self):
        tomorrow = self.today + timedelta(days=1)
        self._job('SRV20990201', assignee=self.tech, date=tomorrow, time=time(9, 0))
        self._job('SRV20990202', assign_all=True, date=tomorrow, time=time(13, 0))
        Notification.objects.all().delete()
        self.assertEqual(field_digest(self.today), 2)
        note = Notification.objects.get(recipient=self.tech_user)
        self.assertTrue(note.title.startswith('Yarın 2 işiniz var'))
        self.assertIn('09:00 Ahmet Yılmaz', note.body)
        self.assertEqual(field_digest(self.today), 0)

    def test_maintenance_heads_up_once_per_due_date(self):
        Device.objects.create(
            party=self.party, name='Split 12000', next_due=self.today + timedelta(days=5), created_by=self.lead
        )
        self.assertEqual(maintenance_heads_up(self.today), 1)
        self.assertEqual(maintenance_heads_up(self.today), 0)
        self.assertEqual(self.kinds(self.lead), [Notification.KIND_MAINTENANCE])
