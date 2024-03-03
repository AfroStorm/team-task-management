from rest_framework.test import APITestCase, APIRequestFactory
from api import models, serializers
from rest_framework import status
from collections import OrderedDict
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TestCustomUserModel(APITestCase):
    """
    Tests related to the CustomUser Model.
    """

    def setUp(self) -> None:
        """
        Creates a set of instances required for this testing class.
        """

        # Category instances
        self.category = models.Category.objects.create(
            name='Human Resource',
            description='This is a category named human resource.'
        )
        # Position instances
        self.position1 = models.Position.objects.create(
            title='Human Resource Specialist',
            description='This is a position titled Human Resource Specialist.',
            is_task_manager=True,
            category=self.category
        )
        self.position2 = models.Position.objects.create(
            title='Human Resource Assistant',
            description='This is a position titled Human Resource Assistant.',
            is_task_manager=False,
            category=self.category
        )
        # User instances
        self.user = User.objects.create(
            user_data={
                'email': 'some.email@example.com',
                'password': 'testpassword123'

            },
            profile_data={
                'first_name': 'John',
                'last_name': 'Doe',
                'position': self.position1
            }
        )
        self.user2 = User.objects.create(
            user_data={
                'email': 'another.email@example.com',
                'password': 'testpassword123'

            },
            profile_data={
                'first_name': 'Rebecca',
                'last_name': 'Brown',
                'position': self.position2
            }
        )
        self.admin = User.objects.create_superuser(
            user_data={
                'email': 'admin.email@example.com',
                'password': 'testpassword123'

            },
            profile_data={
                'first_name': 'Kevin',
                'last_name': 'Smith',
                'position': self.position1
            }
        )
        return super().setUp()

    # Django intern creation
    def test_create_custom_user(self):
        """
        Tests the creation of a CustomUser instance and its related
        UserProfile instance through the CustomUserManager.
        """
        email = 'peterpahn@GMAIL.com'  # not normalized
        password = 'blabla123.'
        first_name = 'Peter'
        last_name = 'Pahn'

        user_data = {
            'email': email,
            'password': password
        }
        profile_data = {
            'first_name': first_name,
            'last_name': last_name,
            'position': self.position1
        }
        user = User.objects.create(user_data, profile_data)

        # USER TESTS
        # Email normalized
        email_domain_part = user.email.split('@')[1]
        expected_email_domain_part = email.split('@')[1].lower()
        self.assertEqual(email_domain_part, expected_email_domain_part)

        # Password got hashed
        self.assertNotEqual(user.password, password)
        # Correct password
        self.assertTrue(user.check_password(password))

        # Correct str representation
        expected_string = f'Email: {email.lower()}'
        actual_string = str(user)
        self.assertEqual(actual_string, expected_string)

        # PROFILE TESTS
        # Profile got created
        self.assertIsNotNone(user.profile)

        # First name correct
        profile = user.profile
        self.assertEqual(profile.first_name, first_name)

        # Last name correct
        self.assertEqual(profile.last_name, last_name)

        # Position got assigned
        self.assertIsNotNone(profile.position)
        self.assertEqual(profile.position, self.position1)

        # Create super user
        user_data['email'] = 'peterlustig@gmail.com'  # Unique key constrain
        superuser = User.objects.create_superuser(user_data, profile_data)

        # Superuser/staff is true
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    # UserInitiationSerializer
    def test_serializer_password_confirmation(self):
        """
        Tests the password validation of the UserInitiationSerializer when
        wrong password data is passed to it, as well as when password
        data is passed to it.
        """

        # Password confirmation fail
        wrong_data = {
            'email': 'peterlustig@gmail.com',
            'password': 'testpassword123',
            'password_confirmation': 'testpassword456',  # Wrong password
            'first_name': 'Peter',
            'last_name': 'Lustig',
            'position': self.position1
        }
        serializer = serializers.UserInitiationSerializer(
            data=wrong_data
        )

        # Catch validation error
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        error_detail = context.exception.detail
        expected_error_detail = {
            'non_field_errors': [
                serializers.ErrorDetail(
                    "Passwords do not match!", code='invalid'
                )
            ]
        }
        # Expected error details
        self.assertEqual(error_detail, expected_error_detail)

        # Password confirmation success
        correct_data = {
            'email': 'peterlustig@gmail.com',
            'password': 'testpassword123',
            'password_confirmation': 'testpassword123',  # Correct password
            'first_name': 'Peter',
            'last_name': 'Lustig',
            'position': self.position1
        }
        serializer = serializers.UserInitiationSerializer(
            data=correct_data
        )
        # Data is valid
        self.assertTrue(serializer.is_valid())

    def test_serializer_create(self):
        """
        Tests if the serializer create method is correctly creating a
        user instance.
        """

        data = {
            'email': 'theemail@gmail.com',
            'password': 'blabla123',
            'password_confirmation': 'blabla123',
            'first_name': 'Kevin',
            'last_name': 'Reiner',
            'position': self.position1.title,
        }
        serializer = serializers.UserInitiationSerializer(
            data=data
        )

        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # valid CustomUser instance
        self.assertIsNotNone(user)
        self.assertIsInstance(user, models.CustomUser)

    def test_serializer_serialization(self):
        """
        Tests if the to_representation method of the
        UserInitiationSerializer presents the data in form of nested
        dictionaries.
        """

        serializer = serializers.UserInitiationSerializer(instance=self.user)
        user = self.user
        profile = self.user.profile
        position = self.user.profile.position
        category = self.user.profile.position.category
        expected_data = {
            'id': user.id,
            'email': user.email,
            'is_active': user.is_active,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'profile': {
                'id': profile.id,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'position': {
                    'id': position.id,
                    'title': position.title,
                    'description': position.description,
                    'is_task_manager': position.is_task_manager,
                    'category': category.name
                },
            },
        }
        # Password not in serializer data
        self.assertNotIn(serializer.data, user.password)
        # Expected structure
        self.assertEqual(serializer.data, expected_data)

    # View tests
    def test_user_create_action(self):
        """
        Tests if the CustomUserVIew is successfully creating a user
        instance and giving the expected responses.
        """

        data = {
            'email': 'uniqueemail@gmail.com',
            'password': 'blabla123',
            'password_confirmation': 'blabla123',
            'first_name': 'Kevin',
            'last_name': 'Reiner',
            'position': self.position1.title,
        }
        url = reverse('customuser-list')

        # PERMISSION TESTS
        # Unauthenticated user
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Non-admin user
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        # Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin user
        self.client.force_authenticate(user=self.admin)
        # Successful request
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Message not None
        message = response.data.get('message')
        self.assertIsNotNone(message)

        # Bad request response
        data['position'] = self.position1.id
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Message not None
        message = response.data.get('message')
        self.assertIsNotNone(message)

    def test_user_update_action(self):
        """
        Tests if the CustomUserView update action works as expected.
        """
        data = {
            'email': 'updateduniqueemail@gmail.com',
            'password': 'blabla456',
            'password_confirmation': 'blabla456',
        }
        url = reverse('customuser-detail', args=[self.user.id])

        # Unauthenticated user
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Non-owner
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin user
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Owner
        self.client.force_authenticate(user=self.user)
        # Successful request
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Message not None
        message = response.data.get('message')
        self.assertIsNotNone(message)

        # Bad request
        data['password'] = 'blabla789'  # Incorrect password
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Message not None
        message = response.data.get('message')
        self.assertIsNotNone(message)

    def test_user_partial_update_action(self):
        """
        Tests if the CustomUserView partial update action works as
        expected.
        """
        data = {
            'password': 'blabla456',
            'password_confirmation': 'blabla456',
        }
        url = reverse('customuser-detail', args=[self.user.id])

        # PERMISSION TESTS
        # Unauthenticated user
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Non-owner
        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin user
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Owner
        self.client.force_authenticate(user=self.user)
        # Successful request
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Message not None
        message = response.data.get('message')
        self.assertIsNotNone(message)
        # Bad request
        data['password'] = 'blabla789'  # Incorrect password
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Message not None
        message = response.data.get('message')
        self.assertIsNotNone(message)

    def test_user_list_action(self):
        """
        Tests if the CustomUserView list action returns a list of user
        instance.
        """

        url = reverse('customuser-list')

        # PERMISSION TESTS
        # Unauthenticated user
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticated user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_retrieve_action(self):
        """
        Tests if the CustomUserView retrieve action works as expected.
        """

        url = reverse('customuser-detail', args=[self.user.id])

        # PERMISSION TESTS
        # Unauthenticated user
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticated user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
