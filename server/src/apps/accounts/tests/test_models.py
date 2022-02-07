from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    data = {"phone_number": "998901234567", "username": "tezbor"}

    def test_create_user_with_unique_phone_number(self):
        """Test creating a new user with an phone number is successful"""

        user = get_user_model().objects.create(
            phone_number=self.data['phone_number'],
        )
        self.assertEqual(user.phone_number, self.data['phone_number'])

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            phone_number=self.data['phone_number'],
            password="test123"
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
