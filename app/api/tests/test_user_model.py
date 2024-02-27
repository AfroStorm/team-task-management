from rest_framework.test import APITestCase, APIRequestFactory
from api import models, serializers
from rest_framework import status
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
            category=self.category
        )
        self.position2 = models.Position.objects.create(
            title='Human Resource Assistant',
            description='This is a position titled Human Resource Assistant.',
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
        return super().setUp()

    # Django intern creation
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
            'last_name': last_name,
            'position': self.position1
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
        # Correct str representation
        expected_string = f'Email: {email}'
        actual_string = str(user)
        self.assertEqual(actual_string, expected_string)

        # PROFILE TESTS
        # Profile got created
        self.assertIsNotNone(user.profile)
        profile = user.profile
        # First name correct
        self.assertEqual(profile.first_name, first_name)
        # Last name correct
        self.assertEqual(profile.last_name, last_name)
        # Position got assigned
        self.assertIsNotNone(profile.position)
        self.assertEqual(profile.position, self.position1)

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
            'last_name': last_name,
            'position': self.position1
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
        # Correct str representation
        expected_string = f'Email: {email}'
        actual_string = str(superuser)
        self.assertEqual(actual_string, expected_string)

        # PROFILE TESTS
        # Profile got created
        self.assertIsNotNone(superuser.profile)
        profile = superuser.profile
        # First name correct
        self.assertEqual(profile.first_name, first_name)
        # Last name correct
        self.assertEqual(profile.last_name, last_name)
        # Position got assigned
        self.assertIsNotNone(profile.position)
        self.assertEqual(profile.position, self.position1)

    # Serializer tests
    def test_serializer_restructuring_data(self):
        """
        Tests if the CustomUserSerializer to_internal_value method is
        correctly restructuring the data into 2 nested dictionaries
        within the original data dictionary (data[user_data],
        data[profile_data])
        """
        data = {
            'email': 'peterlustig@gmail.com',
            'password': 'testpassword123',
            'password_confirmation': 'testpassword123',
            'first_name': 'Peter',
            'last_name': 'Lustig',
            'position': self.position1
        }

        serializer = serializers.CustomUserSerializer()

        restructured_data = serializer.to_internal_value(data)
        expected_data = {
            'user_data': {
                'email': 'peterlustig@gmail.com',
                'password': 'testpassword123',
                'password_confirmation': 'testpassword123',
            },
            'profile_data': {
                'first_name': 'Peter',
                'last_name': 'Lustig',
                'position': self.position1,
            }
        }

        self.assertEqual(restructured_data, expected_data)

    def test_serializer_password_confirmation(self):
        """
        Tests the password validation of the CustomUserSerializer when
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
        serializer = serializers.CustomUserSerializer(
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
        # Correct error details
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
        serializer = serializers.CustomUserSerializer(
            data=correct_data
        )
        # Data is valid
        self.assertTrue(serializer.is_valid())

    def test_serializer_create(self):
        """
        Tests the correct restructuring of the validated data within
        the CustomUserSerializer create method.
        """

        data = {
            'user_data': {
                'email': 'updated.email@gmail.com',
                'password': 'blabla123',
            },
            'profile_data': {
                'first_name': 'Jay',
                'last_name': 'Miller',
                'position': self.position1,
            }
        }

        serializer = serializers.CustomUserSerializer()
        new_user = serializer.create(data)
        # Is valid instance
        self.assertIsInstance(new_user, models.CustomUser)

    def test_serializer_update(self):
        """
        Tests the correct restructuring of the validated data within
        the CustomUserSerializer update method.
        """

        data = {
            'user_data': {
                'email': 'updated.email@gmail.com',
                'password': 'blabla123',
            },
            'profile_data': {
                'first_name': 'Jay',
                'last_name': 'Miller',
                'position': self.position2,
            }
        }

        serializer = serializers.CustomUserSerializer()
        updated_user = serializer.update(
            instance=self.user,
            validated_data=data
        )
        # valid CustomUser instance
        self.assertIsInstance(updated_user, models.CustomUser)
        profile = updated_user.profile
        # Correct email
        email = data['user_data']['email']
        self.assertEqual(updated_user.email, email)
        # Password got hashed
        # Correct password
        password = data['user_data']['password']
        self.assertNotEqual(updated_user.password, password)
        self.assertTrue(updated_user.check_password(password))
        # Correct first_name
        first_name = data['profile_data']['first_name']
        self.assertEqual(profile.first_name, first_name)
        # Correct last_name
        last_name = data['profile_data']['last_name']
        self.assertEqual(profile.last_name, last_name)
        # Position got assigned
        position = data['profile_data']['position']
        self.assertIsNotNone(profile.position)
        self.assertEqual(profile.position, self.position2)

    def test_serializer_represents_nested_dictionaries(self):
        """
        Tests if the to_representation method of the
        CustomUserSerializer presents the data in form of nested
        dictionaries.
        """

        serializer = serializers.CustomUserSerializer(instance=self.user)
        user = self.user
        profile = self.user.profile
        position = self.user.profile.position
        category = self.user.profile.position.category
        expected_data = {
            'id': user.id,
            'email': user.email,
            'last_login': user.last_login,
            'is_active': user.is_active,
            'profile': {
                'id': profile.id,
                'owner': profile.owner.id,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'position': {
                    'id': position.id,
                    'title': position.title,
                    'description': position.description,
                    'is_task_manager': position.is_task_manager,
                    'category': {
                        'id': category.id,
                        'name': category.name,
                        'description': category.description,

                    },
                },
            },
        }
        self.assertEqual(serializer.data, expected_data)
