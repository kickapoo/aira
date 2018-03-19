from django.test import TestCase
from django.contrib.auth.models import User
from aira.models import Profile


class UserTestCase(TestCase):

    def setUp(self):
        self.assertEqual(Profile.objects.count(), 0)
        registered_user_data = {
            'username': 'batman',
            'email': 'batman@cave.com',
            'password': 'thegoatandthesheep',
            'is_active': True
        }
        self.user = User.objects.create(**registered_user_data)

    def test_create_user_profile_receiver(self):
        self.assertEqual(hasattr(self.user, 'profile'), True)

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
