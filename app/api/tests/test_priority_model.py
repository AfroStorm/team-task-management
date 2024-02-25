from rest_framework.test import APITestCase, APIRequestFactory
from api import models
from rest_framework import status
from django.contrib.auth import get_user_model


class TestPriorityModel(APITestCase):
    """
    Tests related to the Priority Model.
    """

    def test_create_priority_model(self):
        """
        Tests the creation of a Priority instance.
        """

        caption = 'High Priority'
        priority_instance = models.Priority.objects.create(caption=caption)

        # Correct caption
        expected_caption = caption
        actual_caption = priority_instance.caption
        self.assertEqual(actual_caption, expected_caption)
        # Correct str representation
        expected_string = f'{caption}'
        actual_string = str(priority_instance)
        self.assertEqual(actual_string, expected_string)
