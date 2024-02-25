from rest_framework.test import APITestCase, APIRequestFactory
from api import models
from rest_framework import status
from django.contrib.auth import get_user_model


class TestCategoryModel(APITestCase):
    """
    Tests related to the Category Model.
    """

    def test_create_category_model(self):
        """
        Tests the creation of a Category instance.
        """

        name = 'Human Resource'
        description = '''A domain specialized in the area of employee
                         recruitment and relationship'''

        category_instance = models.Category.objects.create(
            name=name,
            description=description
        )

        # Correct name
        expected_name = name
        actual_name = category_instance.name
        self.assertEqual(actual_name, expected_name)
        # Correct description
        expected_description = description
        actual_description = category_instance.description
        self.assertEqual(actual_description, expected_description)
        # Correct str representation
        expected_string = f'{name}'
        actual_string = str(category_instance)
        self.assertEqual(actual_string, expected_string)
