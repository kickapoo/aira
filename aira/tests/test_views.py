from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail


class TestIndexPageView(TestCase):

    def test_index_view(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_registration_link_when_anonymous_on_index_view(self):
        resp = self.client.get('/')
        self.assertContains(resp, 'Register')

    def test_no_registration_link_when_logged_on_index_view(self):
        testuser = User.objects.create_user(username='testuser',
                                            email='test@example.com',
                                            password='topsecret')
        testuser.is_active = True
        testuser.save()
        resp = self.client.login(username='testuser', password='topsecret')
        self.assertTrue(resp)
        resp = self.client.get('/')
        self.assertTemplateUsed(resp, 'aira/index.html')
        self.assertNotContains(resp, 'Register')


class TestHomePageView(TestCase):

    def test_home_view_denies_anynomous(self):
        resp = self.client.get('/home/', follow=True)
        self.assertRedirects(resp, '/accounts/login/?next=/home/')

    def test_home_view_loads_user(self):
        testuser = User.objects.create_user(username='testuser',
                                            email='test@example.com',
                                            password='topsecret')
        testuser.is_active = True
        testuser.save()
        resp = self.client.login(username='testuser', password='topsecret')
        self.client.login(username='testuser', password='topsecret')
        resp = self.client.get('/home/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'aira/home.html')


class TestRegistrationView(TestCase):

    def test_registration_form_view(self):
        resp = self.client.get('/accounts/register/')
        self.assertContains(resp, 'action="/accounts/register/')
        self.assertTemplateUsed(resp, 'registration/registration_form.html')

    def test_registration_form_success_redirect_and_sent_mail(self):
        resp = self.client.post('/accounts/register/',
                                {'username': 'testregistser',
                                 'email': 'testregister@example.com',
                                 'password1': 'topsecret',
                                 'password2': 'topsecret'})

        self.assertRedirects(resp, '/accounts/register/complete/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'example.com: Please activate your account.')
