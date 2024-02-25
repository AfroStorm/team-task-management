from rest_framework.test import APITestCase, APIRequestFactory
from api import models
from rest_framework import status
from django.contrib.auth import get_user_model


User = get_user_model()


class TestUserProfileModel(APITestCase):
    """
    Tests related to the UserProfile Model.
    """

    def setUp(self) -> None:
        """
        Necessary models for the creation of a UserProfile instance.
        """
        # Foreign key Category Instance for the position instance
        name = 'Human Resource'
        description = '''A domain specialized in the area of employee
                         recruitment and relationship'''

        self.category_instance = models.Category.objects.create(
            name=name,
            description=description
        )

        # Foreign key Position Instance for the task instance
        title = 'Human Resource Specialist'
        description = '''A Position specialized in the area of employee
                         recruitment and relationship'''
        is_task_manager = True

        self.position_instance = models.Position.objects.create(
            title=title,
            description=description,
            is_task_manager=is_task_manager,
            category=self.category_instance
        )

        return super().setUp()

    def test_create_userprofile_model(self):
        """
        Tests the creation of a UserProfile instance.
        """

        # Foreign key CostumUser Instance
        # UserProfile gets created for each CustomUser through
        # CustomUserManager
        email = 'peterpahn@gmail.com'
        password = 'blabla123.'
        first_name = 'Peter'
        last_name = 'Pahn'
        position = self.position_instance

        user_data = {
            'email': email,
            'password': password
        }
        profile_data = {
            'first_name': first_name,
            'last_name': last_name,
            'position': position,
        }
        user = User.objects.create(user_data, profile_data)

        # Profile got created
        self.assertIsNotNone(user.profile)
        profile = user.profile
        # First name correct
        self.assertEqual(profile.first_name, first_name)
        # Last name correct
        self.assertEqual(profile.last_name, last_name)
        # Position correct
        self.assertIsNotNone(profile.position)
        self.assertEqual(profile.position, position)
        # Correct str representation
        expected_string = f'Profile Owner: {user.email}'
        actual_string = str(profile)
        self.assertEqual(actual_string, expected_string)
