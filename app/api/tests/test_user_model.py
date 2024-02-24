from rest_framework.test import APITestCase, APIRequestFactory
from api import models
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class TestCustomUserMosel(APITestCase):
    """
    Tests related to the CustomUser Model.
    """

    def test_create_custom_user(self):
        """
        Tests the creation of a CustomUser instance and its related
        UserProfile instance through the CustomUserManager.
        """
        email = 'peterpahn@gmail.com'
        password = 'blabla123.'
        first_name = 'Peter'
        last_name = 'Pahn'

        user_data = {
            'email': email,
            'password': password
        }
        profile_data = {
            'first_name': first_name,
            'last_name': last_name
        }
        user = User.objects.create(user_data, profile_data)

        # USER TESTS
        # Email normalized
        email_domain_part = user.email.split('@')[1]
        expected_email_domain_part = email.split('@')[1]
        self.assertEqual(email_domain_part, expected_email_domain_part)
        # Password got hashed
        self.assertNotEqual(user.password, password)
        # Correct password
        self.assertTrue(user.check_password(password))

        # PROFILE TESTS
        # Profile got created
        self.assertIsNotNone(user.profile)
        profile = user.profile
        # First name correct
        self.assertEqual(profile.first_name, first_name)
        # Last name correct
        self.assertEqual(profile.last_name, last_name)

    def test_create_super_user(self):
        """
        Tests the creation of a superuser instance and its related
        UserProfile instance through the CustomUserManager.
        """
        email = 'peterlustig@gmail.com'
        password = 'blabla123.'
        first_name = 'Peter'
        last_name = 'Lustig'

        user_data = {
            'email': email,
            'password': password
        }
        profile_data = {
            'first_name': first_name,
            'last_name': last_name
        }
        superuser = User.objects.create_superuser(user_data, profile_data)

        # USER TESTS
        # Email normalized
        email_domain_part = superuser.email.split('@')[1]
        expected_email_domain_part = email.split('@')[1]
        self.assertEqual(email_domain_part, expected_email_domain_part)
        # Password got hashed
        self.assertNotEqual(superuser.password, password)
        # Correct password
        self.assertTrue(superuser.check_password(password))
        # Superuser/staff is true
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

        # PROFILE TESTS
        # Profile got created
        self.assertIsNotNone(superuser.profile)
        profile = superuser.profile
        # First name correct
        self.assertEqual(profile.first_name, first_name)
        # Last name correct
        self.assertEqual(profile.last_name, last_name)
