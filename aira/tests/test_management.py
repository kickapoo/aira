#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO
from aira.models import CropType, IrrigationType


class PopulateCoeffsTestGRVersion(TestCase):

    def setUp(self):
        self.out = StringIO()
        call_command("populate_coeffs_el", stdout=self.out)

    def test_output_text_on_import_success(self):
        self.assertIn("Aira Coefficients Greek Vr import: Success",
                      self.out.getvalue())

    def test_import_against_database_values_for_crop_csv(self):
        # Values in db models have ordering by name
        # Model.objects.all() will fetch this ordering
        # Sample Data are ordered by name first and last record
        csv_croplines = {
            "first": {
                "name": "Αγγουράκι - Μηχανικής συγκομιδής (Cucumber - Machine Harvest)",
                "category": 4,
            },
            "last": {
                "name": "Χλοοτάπητας ψυχρόφιλος (Turf grass - cool season)",
                "category": 6,
            }
        }
        # Test first record equality
        crop_types = CropType.objects.all()
        first_record = crop_types[0]
        self.assertEqual(first_record.name,
                         csv_croplines["first"]["name"])
        self.assertEqual(first_record.fek_category,
                         csv_croplines["first"]["category"])
        # Test last record equality
        last_record = crop_types.reverse()[0]
        self.assertEqual(last_record.name,
                         csv_croplines["last"]["name"])
        self.assertEqual(last_record.fek_category,
                         csv_croplines["last"]["category"])

    def test_import_against_database_values_for_irrigation_csv(self):
        # Values in db models have ordering by name
        # Model.objects.all() will fetch this ordering
        # Sample Data are ordered by name first and last record
        csv_irrigationlines = {
            "first": {
                "name": "Άρδευση με σταγόνες (Drip irrigation)",
                "efficiency": 0.90
            },
            "last": {
                "name": "Υπόγεια στάγδην άρδευση (Subsurface drip irrigation)",
                "efficiency": 0.95,
            }
        }
        # Test first record equality
        irrigations_types = IrrigationType.objects.all()
        first_record = irrigations_types[0]
        # import ipdb; ipdb.set_trace()
        self.assertEqual(first_record.name,
                         csv_irrigationlines["first"]["name"])
        self.assertEqual(first_record.efficiency,
                         csv_irrigationlines["first"]["efficiency"])
        # Test last record equality
        last_record = irrigations_types.reverse()[0]
        self.assertEqual(last_record.name,
                         csv_irrigationlines["last"]["name"])
        self.assertEqual(last_record.efficiency,
                         csv_irrigationlines["last"]["efficiency"])


class PopulateCoeffsTestEnVersion(TestCase):

    def setUp(self):
        self.out = StringIO()
        call_command("populate_coeffs", stdout=self.out)

    def test_output_text_on_import_success(self):
        self.assertIn("Aira Coefficients Eng Vr import: Success",
                      self.out.getvalue())

    def test_import_against_database_values_for_crop_csv(self):
        # Values in db models have ordering by name
        # Model.objects.all() will fetch this ordering
        # Sample Data are ordered by name first and last record
        csv_croplines = {
            "first": {
                "name": "Alfalfa - for hay",
                "category": 1,
            },
            "last": {
                "name": "Winter Wheat",
                "category": 5,
            }
        }
        # Test first record equality
        crop_types = CropType.objects.all()
        first_record = crop_types[0]
        self.assertEqual(first_record.name,
                         csv_croplines["first"]["name"])
        self.assertEqual(first_record.fek_category,
                         csv_croplines["first"]["category"])
        # Test last record equality
        last_record = crop_types.reverse()[0]
        self.assertEqual(last_record.name,
                         csv_croplines["last"]["name"])
        self.assertEqual(last_record.fek_category,
                         csv_croplines["last"]["category"])

    def test_import_against_database_values_for_irrigation_csv(self):
        # Values in db models have ordering by name
        # Model.objects.all() will fetch this ordering
        # Sample Data are ordered by name first and last record
        csv_irrigationlines = {
            "first": {
                "name": "Drip irrigation",
                "efficiency": 0.9
            },
            "last": {
                "name": "Surface irrigation",
                "efficiency": 0.6,
            }
        }
        # Test first record equality
        irrigations_types = IrrigationType.objects.all()
        first_record = irrigations_types[0]
        # import ipdb; ipdb.set_trace()
        self.assertEqual(first_record.name,
                         csv_irrigationlines["first"]["name"])
        self.assertEqual(first_record.efficiency,
                         csv_irrigationlines["first"]["efficiency"])
        # Test last record equality
        last_record = irrigations_types.reverse()[0]
        self.assertEqual(last_record.name,
                         csv_irrigationlines["last"]["name"])
        self.assertEqual(last_record.efficiency,
                         csv_irrigationlines["last"]["efficiency"])


class DemoUserTest(TestCase):

    def setUp(self):
        self.out = StringIO()
        # Need to populate coeffs before testing demo_user
        call_command("populate_coeffs")
        call_command("demo_user", stdout=self.out)

    def test_command_output(self):
        self.assertIn("Aira Demo user import: Success", self.out.getvalue())
