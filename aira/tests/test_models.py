import datetime as dt
from unittest import mock

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.http.response import Http404
from django.test import TestCase

from model_mommy import mommy

from aira.models import Agrifield, CropType, IrrigationType, Profile


class UserTestCase(TestCase):
    def setUp(self):
        self.assertEqual(Profile.objects.count(), 0)
        self.user = mommy.make(User, username="batman", is_active=True)

    def test_create_user_profile_receiver(self):
        self.assertEqual(hasattr(self.user, "profile"), True)

    def test_created_user_same_profile_FK(self):
        profile = Profile.objects.get(farmer_id=self.user.id)
        self.assertEqual(profile.farmer, self.user)

    def test_save_user_profile_receiver(self):
        self.user.profile.first_name = "Bruce"
        self.user.profile.last_name = "Wayne"
        self.user.profile.address = "Gotham City"
        self.user.save()
        profile = Profile.objects.get(farmer_id=self.user.id)
        self.assertEqual(profile.first_name, "Bruce")
        self.assertEqual(profile.last_name, "Wayne")
        self.assertEqual(profile.address, "Gotham City")


class AgrifieldTestCase(TestCase):
    def setUp(self):

        self.crop_type = mommy.make(
            CropType,
            name="Grass",
            root_depth_max=0.7,
            root_depth_min=1.2,
            max_allow_depletion=0.5,
            fek_category=4,
        )
        self.irrigation_type = mommy.make(
            IrrigationType, name="Surface irrigation", efficiency=0.60
        )
        self.user = mommy.make(User, username="batman", is_active=True)
        self.agrifield = mommy.make(
            Agrifield,
            owner=self.user,
            name="A field",
            crop_type=self.crop_type,
            irrigation_type=self.irrigation_type,
            location=Point(18.0, 23.0),
            area=2000,
        )

    def test_agrifield_creation(self):
        agrifield = Agrifield.objects.create(
            owner=self.user,
            name="A field",
            crop_type=self.crop_type,
            irrigation_type=self.irrigation_type,
            location=Point(18.0, 23.0),
            area=2000,
        )
        self.assertTrue(isinstance(agrifield, Agrifield))
        self.assertEqual(agrifield.__str__(), agrifield.name)

    def test_agrifield_update(self):
        self.agrifield.name = "This another field name"
        self.agrifield.save()
        self.assertEqual(self.agrifield.__str__(), "This another field name")

    def test_agrifield_delete(self):
        self.agrifield.delete()
        self.assertEqual(Agrifield.objects.all().count(), 0)

    def test_valid_user_can_edit(self):
        self.assertTrue(self.agrifield.can_edit(self.user))

    def test_invalid_user_cannot_edit(self):
        joker = mommy.make(User, username="joker", is_active=True)
        with self.assertRaises(Http404):
            self.agrifield.can_edit(joker)

    def test_agrifield_irrigation_optimizer_default_value(self):
        self.assertEqual(self.agrifield.irrigation_optimizer, 0.5)

    def test_agrifield_use_custom_parameters_default_value(self):
        self.assertFalse(self.agrifield.use_custom_parameters)


class CropTypeMostRecentPlantingDateTestCase(TestCase):
    def setUp(self):
        self.crop_type = mommy.make(CropType, planting_date=dt.datetime(1971, 3, 15))

    @mock.patch("aira.models.dt.date")
    def test_result_when_it_has_appeared_this_year(self, m):
        m.today.return_value = dt.datetime(2019, 3, 20)
        m.side_effect = lambda *args, **kwargs: dt.date(*args, **kwargs)
        self.assertEqual(
            self.crop_type.most_recent_planting_date, dt.datetime(2019, 3, 15)
        )

    @mock.patch("aira.models.dt.date")
    def test_result_when_it_has_not_appeared_this_year_yet(self, m):
        m.today.return_value = dt.datetime(2019, 3, 10)
        m.side_effect = lambda *args, **kwargs: dt.date(*args, **kwargs)
        self.assertEqual(
            self.crop_type.most_recent_planting_date, dt.datetime(2018, 3, 15)
        )
