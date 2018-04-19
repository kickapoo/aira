from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO


class DemoUserTest(TestCase):

    def setUp(self):
        self.out = StringIO()
        # Need to populate coeffs before testing demo_user
        call_command("loaddata", "en.json")
        call_command("demo_user", stdout=self.out)

    def test_command_output(self):
        self.assertIn("Aira Demo user import: Success", self.out.getvalue())
