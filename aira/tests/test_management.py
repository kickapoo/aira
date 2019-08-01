from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class DemoUserTest(TestCase):
    def setUp(self):
        self.out = StringIO()
        call_command("demo_user", stdout=self.out)

    def test_command_output(self):
        self.assertIn("Aira Demo user import: Success", self.out.getvalue())
