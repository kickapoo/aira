from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from captcha.models import CaptchaStore
from model_mommy import mommy


class TestIndexPageView(TestCase):

    def setUp(self):
        self.user = mommy.make(
            User,
            username='batman',
            is_active=True,
        )
        # mommy.make is not hashing the password
        self.user.set_password('thegoatandthesheep')
        self.user.save()

    def test_index_view(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_registration_link_when_anonymous_on_index_view(self):
        resp = self.client.get('/')
        self.assertContains(resp, 'Register')

    def test_no_registration_link_when_logged_on_index_view(self):
        resp = self.client.login(username='batman',
                                 password='thegoatandthesheep')
        self.assertTrue(resp)
        resp = self.client.get('/')
        self.assertTemplateUsed(resp, 'aira/index.html')
        self.assertNotContains(resp, 'Register')


class TestHomePageView(TestCase):
    def setUp(self):
        self.user = mommy.make(
            User,
            username='batman',
            is_active=True,
        )
        # mommy.make is not hashing the password
        self.user.set_password('thegoatandthesheep')
        self.user.save()

    def test_home_view_denies_anynomous(self):
        resp = self.client.get('/home/', follow=True)
        self.assertRedirects(resp, '/accounts/login/?next=/home/')

    def test_home_view_loads_user(self):
        self.client.login(username='batman', password='thegoatandthesheep')
        resp = self.client.get('/home/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'aira/home.html')


class TestRegistrationView(TestCase):

    def test_captcha_table_empty(self):
        captcha_count = CaptchaStore.objects.count()
        self.failUnlessEqual(captcha_count, 0)

    def test_registration_form_view(self):
        resp = self.client.get('/accounts/register/')
        self.assertContains(resp, 'action="/accounts/register/')
        self.assertTemplateUsed(resp, 'registration/registration_form.html')

    def test_registration_form_success_redirect_and_sent_mail(self):
        captcha = CaptchaStore.objects.get(hashkey=CaptchaStore.generate_key())
        resp = self.client.post('/accounts/register/',
                                {'username': 'testregistser',
                                 'email': 'testregister@example.com',
                                 'password1': 'topsecret',
                                 'password2': 'topsecret',
                                 'captcha_0': captcha.hashkey,
                                 'captcha_1': captcha.response})
        self.assertRedirects(resp, '/accounts/register/complete/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'example.com: Please activate your account.')
