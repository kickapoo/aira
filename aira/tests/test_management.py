from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO


class PopulateCoeffsTest(TestCase):
    def test_command_output(self):
        out = StringIO()
        call_command('populate_coeffs', stdout=out)
        self.assertIn('Aira database is successfully updated', out.getvalue())


class DemoUserTest(TestCase):
    def test_command_output(self):
        out = StringIO()
        call_command('populate_coeffs', stdout=out)
        call_command('demo_user', stdout=out)
        self.assertIn('Demo User Added', out.getvalue())
