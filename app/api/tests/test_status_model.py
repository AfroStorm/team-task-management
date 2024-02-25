from rest_framework.test import APITestCase, APIRequestFactory
from api import models
from rest_framework import status
from django.contrib.auth import get_user_model


class TestStatusModel(APITestCase):
    """
    Tests related to the Status Model.
    """

    def test_create_status_model(self):
        """
        Tests the creation of a Status instance.
        """

        caption = 'In Progress'
        description = 'Indicates that a task is stillin progress.'

        status_instance = models.Status.objects.create(
            caption=caption,
            description=description
        )

        # Correct caption
        expected_caption = caption
        actual_caption = status_instance.caption
        self.assertEqual(actual_caption, expected_caption)
        # Correct description
        expected_description = description
        actual_description = status_instance.description
        self.assertEqual(actual_description, expected_description)
        # Correct str representation
        expected_string = f'{caption}'
        actual_string = str(status_instance)
        self.assertEqual(actual_string, expected_string)
