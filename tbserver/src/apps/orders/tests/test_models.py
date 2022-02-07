from django.test import TestCase
from django.contrib.auth import get_user_model


# class ModelTests(TestCase):
#
#     def test_create_new_customer_address(self):
#         """Test creating a new user with an email is successful"""
#         username = "tezbor"
#         password = "tezbor123"
#         user = get_user_model().objects.create_user(username=username, password=password)
#
#         self.assertEqual(user.username, username)
#         self.assertTrue(user.check_password(password))
#
#     def test_create_new_agent_address(self):
#         """Test creating user with no email raises error"""
#         with self.assertRaises(ValueError):
#             get_user_model().objects.create_user(None, "tezbor123")
#
#     def test_create_new_superuser(self):
#         """Test creating a new superuser"""
#         user = get_user_model().objects.create_superuser(
#             "tezbor",
#             "tezbor123"
#         )
#         self.assertTrue(user.is_staff)
#         self.assertTrue(user.is_superuser)
