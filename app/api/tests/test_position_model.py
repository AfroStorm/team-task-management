from rest_framework.test import APITestCase, APIRequestFactory
from api import models
from rest_framework import status
from django.contrib.auth import get_user_model


class TestPositionModel(APITestCase):
    """
    Tests related to the Position Model.
    """

    def setUp(self) -> None:
        """
        Necessary models for the creation of a Position instance.
        """

        # Foreign key Category Instance for position instance
        name = 'Human Resource'
        description = '''A domain specialized in the area of employee
                         recruitment and relationship'''

        self.category_instance = models.Category.objects.create(
            name=name,
            description=description
        )
        return super().setUp()

    def test_create_position_model(self):
        """
        Tests the creation of a Position instance.
        """

        title = 'Human Resource Specialist'
        description = '''A Position specialized in the area of employee
                         recruitment and relationship'''
        is_task_manager = True
        category = self.category_instance

        position_instance = models.Position.objects.create(
            title=title,
            description=description,
            is_task_manager=is_task_manager,
            category=category
        )

        # Correct title
        expected_title = title
        actual_title = position_instance.title
        self.assertEqual(actual_title, expected_title)
        # Correct description
        expected_description = description
        actual_description = position_instance.description
        self.assertEqual(actual_description, expected_description)
        # Is_task_manager true
        self.assertTrue(position_instance.is_task_manager)
        # Category assigned correctly
        self.assertIsNotNone(position_instance.category)
        self.assertEqual(position_instance.category, category)
        # Correct str representation
        expected_string = f'{title}'
        actual_string = str(position_instance)
        self.assertEqual(actual_string, expected_string)
