from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO


class PopulateCoeffsTest(TestCase):

    def test_command_gr_verion(self):
        out = StringIO()
        call_command('populate_coeffs_el', stdout=out)
        self.assertIn('Aira Coefficients Greek Vr import: Success',
                      out.getvalue())

    def test_command_en_verion(self):
        out = StringIO()
        call_command('populate_coeffs', stdout=out)
        self.assertIn('Aira Coefficients Eng Vr import: Success',
                      out.getvalue())


class DemoUserTest(TestCase):
    def test_command_output(self):
        out = StringIO()
        call_command('populate_coeffs', stdout=out)
        call_command('demo_user', stdout=out)
        self.assertIn('Aira Demo user import: Success', out.getvalue())
