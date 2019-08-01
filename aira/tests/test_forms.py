from django.test import TestCase


class TestRegistrationForm(TestCase):
    def test_registration_form_submission(self):
        post_data = {"usename": "batman", "password": "thegoatandthesheep"}
        r = self.client.post("/accounts/register/", post_data)
        self.assertEqual(r.status_code, 200)

    def test_registation_form_fails_blank_submission(self):
        r = self.client.post("/accounts/register/", {})
        self.assertFormError(r, "form", "password1", "This field is required.")
