from django.test import TestCase
from django.contrib.auth.models import User


class TestRegistrationForm(TestCase):

    def test_registration_form_submission(self):
        testuser = User.objects.create_user(username='testuser',
                                            email='test@example.com',
                                            password='topsecret')
        testuser.is_active = True
        testuser.save()
        resp = self.client.post('/accounts/register/', {'usename': 'testuser',
                                                        'password': 'topsecret'})
        self.assertEqual(resp.status_code, 200)

    def test_registation_form_fails_blank_submission(self):
        resp = self.client.post('/accounts/register/', {})
        self.assertFormError(resp, 'form', 'password1',
                             'This field is required.')
