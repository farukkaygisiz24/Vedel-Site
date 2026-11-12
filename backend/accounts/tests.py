from django.test import TestCase
from django.urls import reverse

from accounts.models import Customer
from crew.models import CrewMember


class LeadCrewBindTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='lead1',
            password='pass-word',
            first_name='Ömer',
            last_name='Kaygısız',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.other = Customer.objects.create_user(
            username='lead2',
            password='pass-word',
            first_name='Samet',
            last_name='Aydın',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.card = CrewMember.objects.create(
            number='PER-0099',
            first_name='Ömer Faruk',
            last_name='Kaygısız',
            phone='05551112233',
            created_by=self.lead,
        )

    def _save(self, actor, account, **extra):
        self.client.force_login(actor)
        data = {
            'action': 'save',
            'first_name': account.first_name,
            'last_name': account.last_name,
            'email': account.email,
            'phone': account.phone,
            'role': account.role,
        }
        data.update(extra)
        return self.client.post(account.get_absolute_url(), data)

    def test_self_edit_shows_crew_picker(self):
        self.client.force_login(self.lead)
        page = self.client.get(self.lead.get_absolute_url())
        body = page.content.decode()
        self.assertIn('name="crew_id"', body)
        self.assertIn(self.card.number, body)
        self.assertNotIn('id="user-crew-fields" hidden', body)

    def test_lead_binds_own_crew_card(self):
        resp = self._save(self.lead, self.lead, crew_id=str(self.card.pk))
        self.assertEqual(resp.status_code, 302)
        self.card.refresh_from_db()
        self.assertEqual(self.card.user_id, self.lead.pk)

    def test_other_lead_can_bind_card(self):
        resp = self._save(self.other, self.lead, crew_id=str(self.card.pk))
        self.assertEqual(resp.status_code, 302)
        self.card.refresh_from_db()
        self.assertEqual(self.card.user_id, self.lead.pk)

    def test_service_role_requires_crew(self):
        tech = Customer.objects.create_user(
            username='tech1',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SALES,
        )
        resp = self._save(self.lead, tech, role=Customer.ROLE_SERVICE)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('personel kartına bağlanır', resp.content.decode())


class FieldWebAppTests(TestCase):
    def setUp(self):
        self.user = Customer.objects.create_user(
            username='field-app',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        CrewMember.objects.create(
            number='CRWAPP1',
            first_name='Saha',
            last_name='App',
            phone='05551112233',
            user=self.user,
            created_by=self.user,
        )

    def test_anon_manifest_starts_at_login(self):
        resp = self.client.get(reverse('portal-manifest'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'].split(';')[0], 'application/manifest+json')
        data = resp.json()
        self.assertEqual(data['scope'], '/')
        self.assertEqual(data['display'], 'standalone')
        self.assertEqual(data['start_url'], reverse('portal-login'))

    def test_manifest_scope_covers_settings(self):
        self.client.force_login(self.user)
        data = self.client.get(reverse('portal-manifest')).json()
        self.assertEqual(data['scope'], '/')
        self.assertEqual(data['start_url'], reverse('portal-field'))

    def test_field_settings_stays_in_webapp(self):
        self.client.force_login(self.user)
        body = self.client.get(reverse('portal-settings')).content.decode()
        self.assertIn('rel="manifest"', body)
        self.assertIn('navigator.standalone', body)
        self.assertIn(reverse('portal-settings'), body)
        self.assertIn('apple-mobile-web-app-capable', body)
        self.assertIn('--browser-bar', body)


class LoginRedirectTests(TestCase):
    def setUp(self):
        self.lead = Customer.objects.create_user(
            username='login-lead',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE_LEAD,
        )
        self.tech = Customer.objects.create_user(
            username='login-tech',
            password='pass-word',
            is_staff=True,
            role=Customer.ROLE_SERVICE,
        )
        CrewMember.objects.create(
            number='CRWLOGIN1',
            first_name='Saha',
            last_name='Giris',
            phone='05551112233',
            user=self.tech,
            created_by=self.lead,
        )

    def _json_login(self, username):
        return self.client.post(
            reverse('portal-login'),
            {'username': username, 'password': 'pass-word'},
            HTTP_ACCEPT='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

    def test_login_page_has_no_fake_shell(self):
        page = self.client.get(reverse('portal-login'))
        self.assertEqual(page.status_code, 200)
        body = page.content.decode()
        self.assertIn('Giriş yapın', body)
        self.assertIn('location.replace(result.data.redirect)', body)
        self.assertNotIn('Hoş geldiniz', body)
        self.assertNotIn('welcome-title', body)
        self.assertNotIn('force_home', body)
        self.assertNotIn('class="workspace"', body)
        self.assertNotIn('class="is-app"', body)
        self.assertNotIn('class="app-only"', body)
        self.assertNotIn('class="main-col"', body)

    def test_office_json_login_redirects_to_dashboard(self):
        resp = self._json_login('login-lead')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['ok'])
        self.assertFalse(data['field'])
        self.assertEqual(data['redirect'], reverse('portal-dashboard'))
        self.assertEqual(data['username'], 'login-lead')

    def test_field_json_login_redirects_to_field(self):
        resp = self._json_login('login-tech')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['ok'])
        self.assertTrue(data['field'])
        self.assertEqual(data['redirect'], reverse('portal-field'))
