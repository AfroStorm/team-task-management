from rest_framework.test import APITestCase, APIRequestFactory
from api import models, serializers
from rest_framework import status
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class TestTaskModel(APITestCase):
    """
    Tests related to the Task Model.
    """

    def setUp(self) -> None:
        """
        Necessary models for the creation of a Task instance.
        """
        # Foreign key Category Instance for the position/task instance
        self.category_instance = models.Category.objects.create(
            name='Human Resource',
            description='''A domain specialized in the area of employee
                         recruitment and relationship'''
        )

        # Foreign key Position Instance for the userprofile instance
        self.position_instance = models.Position.objects.create(
            title='Human Resource Specialist',
            description='''A Position specialized in the area of employee
                         recruitment and relationship''',
            is_task_manager=True,
            category=self.category_instance
        )

        # Foreign key Priority instance for the task instance
        self.priority_instance = models.Priority.objects.create(
            caption='High Priority'
        )

        # Foreign key Status instance for the task instance
        self.status_instance = models.Status.objects.create(
            caption='In Progress',
            description='Indicates that a task is stillin progress.'
        )

        # Task team_members/owner = UserProfile
        # -> automatically created with CustomUser (CustomUserManager)

        # User as owner for task
        user_data = {
            'email': 'peterpahn@gmail.com',
            'password': 'blabla123.'
        }
        profile_data = {
            'first_name': 'Peter',
            'last_name': 'Pahn',
            'position': self.position_instance,
        }
        self.owner = User.objects.create(user_data, profile_data)

        # User as team_member for task.team_members
        user_data = {
            'email': 'tinaturner@gmail.com',
            'password': 'blabla123.'
        }
        profile_data = {
            'first_name': 'Tina',
            'last_name': 'Turner',
            'position': self.position_instance,
        }
        self.team_member = User.objects.create(user_data, profile_data)

        # User as unrelated user to the Task
        user_data = {
            'email': 'michael.jackson@gmail.com',
            'password': 'blabla123.'
        }
        profile_data = {
            'first_name': 'Michael',
            'last_name': 'Jackson',
            'position': self.position_instance,
        }
        self.task_unrelated_user = User.objects.create(
            user_data, profile_data
        )

        # Admin user
        user_data = {
            'email': 'christian@gmail.com',
            'password': 'blabla123.'
        }
        profile_data = {
            'first_name': 'Christian',
            'last_name': 'Wagner',
            'position': self.position_instance,
        }
        self.admin = User.objects.create_superuser(user_data, profile_data)

        # Task instances
        self.task = models.Task.objects.create(
            title='New Task Instance',
            description='A new task created for testing',
            due_date=timezone.now() + timezone.timedelta(days=3),
            completed_at=timezone.now() + timezone.timedelta(days=1),
            category=self.category_instance,
            priority=self.priority_instance,
            status=self.status_instance,
            owner=self.owner.profile
        )
        # created_at = auto_now_add
        self.task.team_members.add(self.team_member.profile)

        # Task without team members
        self.no_team_task = models.Task.objects.create(
            title='No Team Task Instance',
            description='A new task created for testing',
            due_date=timezone.now() + timezone.timedelta(days=8),
            completed_at=timezone.now() + timezone.timedelta(days=5),
            category=self.category_instance,
            priority=self.priority_instance,
            status=self.status_instance,
            owner=self.owner.profile
        )
        return super().setUp()

    # # Django intern creation
    # def test_create_task_model(self):
    #     """
    #     Tests the creation of a Task instance.
    #     """

    #     title = 'New Task Instance'
    #     description = 'A new task created for testing'
    #     due_date = timezone.now() + timezone.timedelta(days=3)
    #     # created_at = auto_now_add
    #     completed_at = timezone.now() + timezone.timedelta(days=1)
    #     category = self.category_instance
    #     priority = self.priority_instance
    #     status = self.status_instance
    #     owner = self.owner.profile
    #     team_member = self.team_member.profile

    #     task = models.Task.objects.create(
    #         title=title,
    #         description=description,
    #         due_date=due_date,
    #         completed_at=completed_at,
    #         category=category,
    #         priority=priority,
    #         status=status,
    #         owner=owner
    #     )
    #     task.team_members.add(team_member)

    #     # Title correct
    #     self.assertEqual(task.title, title)
    #     # Description correct
    #     self.assertEqual(task.description, description)
    #     # Due_date correct
    #     self.assertEqual(task.due_date, due_date)
    #     # Created correct
    #     created_at_date = task.created_at.date()
    #     created_at = timezone.now().date()  # expected
    #     self.assertEqual(created_at_date, created_at)
    #     # Completed_at correct
    #     completed_at_date = task.completed_at.date()
    #     completed_at = completed_at.date()  # expected
    #     self.assertEqual(completed_at_date, completed_at)
    #     # Category correct
    #     self.assertEqual(task.category, category)
    #     # Priority correct
    #     self.assertEqual(task.priority, priority)
    #     # Status correct
    #     self.assertEqual(task.status, status)
    #     # Owner correct
    #     self.assertEqual(task.owner, owner)
    #     # Team member correct
    #     task_team_member = task.team_members.get(id=team_member.id)
    #     self.assertEqual(task_team_member, team_member)
    #     # Correct str representation
    #     expected_string = f'ID: {task.id} - Status: {status} - Title: {title}'
    #     actual_string = str(task)
    #     self.assertEqual(actual_string, expected_string)

    # # TaskSerializer tests
    # def test_serialization(self):
    #     """
    #     Tests if the TaskSerializer only shows tasks to
    #     - Task team_members
    #     - Task owner
    #     - Staff users.

    #     Also if shows team_members/owner as CustomUser.email
    #     """

    #     # Preparing dates to be compared with serializer dates
    #     due_date = self.task.due_date.strftime(
    #         '%Y-%m-%dT%H:%M:%S.%fZ'
    #     )
    #     completed_at = self.task.completed_at.strftime(
    #         '%Y-%m-%dT%H:%M:%S.%fZ'
    #     )
    #     created_at = self.task.created_at.strftime(
    #         '%Y-%m-%dT%H:%M:%S.%fZ'
    #     )

    #     expected_data = {
    #         'id': self.task.id,
    #         'title': self.task.title,
    #         'description': self.task.description,
    #         'due_date': due_date,
    #         'created_at': created_at,
    #         'completed_at': completed_at,
    #         'category': self.task.category.name,
    #         'priority': self.task.priority.caption,
    #         'status': self.task.status.caption,
    #         'owner': self.owner.email,
    #         'team_members': [self.team_member.email],
    #     }

    #     # Creating request
    #     url = reverse('task-list')
    #     api_factory = APIRequestFactory()
    #     request = api_factory.get(url)

    #     # Task owner
    #     request.user = self.owner
    #     serializer = serializers.TaskSerializer(
    #         instance=self.task,
    #         context={'request': request}
    #     )
    #     self.assertEqual(serializer.data, expected_data)

    #     # Task team member
    #     request.user = self.team_member
    #     serializer = serializers.TaskSerializer(
    #         instance=self.task,
    #         context={'request': request}
    #     )
    #     self.assertEqual(serializer.data, expected_data)

    #     # Admin
    #     request.user = self.admin
    #     serializer = serializers.TaskSerializer(
    #         instance=self.task,
    #         context={'request': request}
    #     )
    #     self.assertEqual(serializer.data, expected_data)

    #     # Task unrelated user
    #     request.user = self.task_unrelated_user
    #     serializer = serializers.TaskSerializer(
    #         instance=self.task,
    #         context={'request': request}
    #     )
    #     self.assertEqual(serializer.data, {})

    # def test_serializer_update(self):
    #     """
    #     Tests if the TaskSerializer correctly updates the Task
    #     fields.
    #     """

    #     category_update = models.Category.objects.create(
    #         name='Information Technology',
    #         description='''A domain specialized in the area of information
    #                      technology'''
    #     )
    #     priority_update = models.Priority.objects.create(
    #         caption='Low Priority'
    #     )
    #     status_update = models.Status.objects.create(
    #         caption='In Completed',
    #         description='Indicates that a task is completed.'
    #     )
    #     data = {
    #         'title': 'Updated Task Title',
    #         'description': 'Updated task description.',
    #         'due_date': timezone.now() + timezone.timedelta(days=5),
    #         'completed_at': timezone.now() + timezone.timedelta(days=7),
    #         'category': category_update.name,
    #         'priority': priority_update.caption,
    #         'status': status_update.caption,
    #     }

    #     # Preparing dates to be compared with serializer dates
    #     due_date = data.get('due_date').strftime(
    #         '%Y-%m-%dT%H:%M:%S.%fZ'
    #     )
    #     completed_at = data.get('completed_at').strftime(
    #         '%Y-%m-%dT%H:%M:%S.%fZ'
    #     )
    #     created_at = self.task.created_at.strftime(
    #         '%Y-%m-%dT%H:%M:%S.%fZ'
    #     )
    #     expected_data = {
    #         'id': self.task.id,
    #         'title': data.get('title'),
    #         'description': data.get('description'),
    #         'due_date': due_date,
    #         'created_at': created_at,
    #         'completed_at': completed_at,
    #         'category': category_update.name,
    #         'priority': priority_update.caption,
    #         'status': status_update.caption,
    #         'owner': self.owner.email,
    #         'team_members': [self.team_member.email],
    #     }

    #     serializer = serializers.TaskSerializer(
    #         instance=self.task,
    #         data=data,
    #         partial=True
    #     )

    #     # Valid data
    #     self.assertTrue(serializer.is_valid())
    #     # Is Task instance
    #     updated_task = serializer.save()
    #     self.assertTrue(isinstance(updated_task, models.Task))
    #     # Fields correctly updated
    #     updated_data = serializers.TaskSerializer(instance=updated_task).data
    #     self.assertEqual(updated_data, expected_data)

    # def test_serializer_create(self):
    #     """
    #     Tests if the TaskSerializer creates valid Task instances.
    #     """

    #     new_category = models.Category.objects.create(
    #         name='Information Technology',
    #         description='''A domain specialized in the area of information
    #                      technology'''
    #     )
    #     new_priority = models.Priority.objects.create(
    #         caption='Low Priority'
    #     )
    #     new_status = models.Status.objects.create(
    #         caption='In Completed',
    #         description='Indicates that a task is completed.'
    #     )
    #     data = {
    #         'title': 'New Task Title',
    #         'description': 'New task description.',
    #         'due_date': timezone.now() + timezone.timedelta(days=5),
    #         'completed_at': timezone.now() + timezone.timedelta(days=7),
    #         'category': new_category.name,
    #         'priority': new_priority.caption,
    #         'status': new_status.caption
    #     }

    #     serializer = serializers.TaskSerializer(
    #         data=data,
    #     )

    #     # Valid data
    #     self.assertTrue(serializer.is_valid())
    #     # Normally the owner gets added within the perform create of
    #     # the TaskVIew to bypass the read only restriction
    #     serializer.validated_data['owner'] = self.owner.profile
    #     # Is Task instance
    #     updated_task = serializer.save()
    #     self.assertTrue(isinstance(updated_task, models.Task))

    # def test_serializer_read_only_fields(self):
    #     """
    #     Tests if the TaskSerializer has write_only true on

    #     - owner
    #     - created_at
    #     - team_members
    #     - task_resource.
    #     """

    #     def check_read_only(request):
    #         """
    #         Checks the read only fields for

    #         - Task owner
    #         - Admin
    #         - Team member
    #         """

    #         serializer = serializers.TaskSerializer(
    #             instance=self.task,
    #             context={'request': request}
    #         )
    #         fields = serializer.fields

    #         # Admin
    #         if request.user == self.admin:
    #             read_only_fields = ['created_at', 'id']
    #             for field in fields:
    #                 if field in read_only_fields:
    #                     self.assertTrue(fields.get(field).read_only)
    #                 else:
    #                     self.assertFalse(fields.get(field).read_only)

    #         # Task owner/team_member
    #         else:
    #             read_only_fields = [
    #                 'created_at', 'owner', 'id', 'team_members',
    #                 'task_resource'
    #             ]
    #             for field in fields:
    #                 if field in read_only_fields:
    #                     self.assertTrue(fields.get(field).read_only)
    #                 else:
    #                     self.assertFalse(fields.get(field).read_only)

    #     url = reverse('task-list')
    #     api_factory = APIRequestFactory()
    #     request = api_factory.get(url)

    #     request_users = [self.owner, self.team_member, self.admin]
    #     for user in request_users:
    #         request.user = user
    #         check_read_only(request)

    # # View tests
    def test_view_add_team_member(self):
        """
        Tests if action is adding a CustomUser to the Task instance.
        Only allows:
        - Task.owner
        - Admin
        """

        url = reverse('task-add_team_member', args=[self.no_team_task.id])
        data = {
            'team_members': [self.task_unrelated_user.id]
        }

        # UNAUTHENTICATED
        response = self.client.patch(url, data, format='json')
        # Correct status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # ADMIN
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(url, data, format='json')
        # Correct status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # TASK OWNER
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(url, data, format='json')

        # Correct status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Team member added
        retrieved_team = response.data.get('team_members')
        expected_team = [
            self.task_unrelated_user.email
        ]
        self.assertEqual(retrieved_team, expected_team)
        # Message not None
        message = response.data.get('message')
        self.assertIsNotNone(message)

        # Bad request
        data['team_members'] = ['9']
        response = self.client.patch(url, data, format='json')
        # debugg
        print(f'RESPONSE DATA: {response.data}')
        # Correct status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Message not None
        message = response.data.get('message')
        self.assertIsNotNone(message)

    # def test_view_remove_team_member(self):
    #     """
    #     Tests if action is removing a CustomUser from the Task
    #     instance.
    #     Only allows:
    #     - Task.owner
    #     - Admin
    #     """

    #     url = reverse('task-remove_team_member', args=[self.task.id])
    #     data = {
    #         'team_member': self.team_member.profile.id
    #     }

    #     # UNAUTHENTICATED
    #     response = self.client.delete(url, data, format='json')
    #     # Correct status code
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    #     # ADMIN
    #     self.client.force_authenticate(user=self.admin)
    #     response = self.client.delete(url, data, format='json')
    #     # Correct status code
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    #     # Add removed team member again for testing
    #     self.task.team_members.add(self.team_member.profile)

    #     # TASK OWNER
    #     self.client.force_authenticate(user=self.owner)
    #     response = self.client.delete(url, data, format='json')

    #     # Correct status code
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # Team member removed
    #     retrieved_team = response.data.get('team_members')
    #     expected_team = []
    #     self.assertEqual(retrieved_team, expected_team)
    #     # Message not None
    #     message = response.data.get('message')
    #     self.assertIsNotNone(message)

    #     # Add removed team member again for testing
    #     self.task.team_members.add(self.team_member.profile)

    #     # Bad request
    #     data['team_member'] = 'wrong.email@gmail.com'
    #     response = self.client.delete(url, data, format='json')
    #     # Correct status code
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     # Message not None
    #     message = response.data.get('message')
    #     self.assertIsNotNone(message)

    # def test_view_create(self):
    #     """
    #     Tests if the perform create method of the TaskView assigns
    #     the reques.user.profile as Task.owner
    #     """

    #     # Preparing request data
    #     new_category = models.Category.objects.create(
    #         name='Information Technology',
    #         description='''A domain specialized in the area of information
    #                      technology'''
    #     )
    #     new_priority = models.Priority.objects.create(
    #         caption='Low Priority'
    #     )
    #     new_status = models.Status.objects.create(
    #         caption='In Completed',
    #         description='Indicates that a task is completed.'
    #     )
    #     request_data = {
    #         'title': 'New Task Title',
    #         'description': 'New task description.',
    #         'due_date': timezone.now() + timezone.timedelta(days=5),
    #         'completed_at': timezone.now() + timezone.timedelta(days=7),
    #         'category': new_category.name,
    #         'priority': new_priority.caption,
    #         'status': new_status.caption
    #     }
    #     url = reverse('task-list')

    #     # --PERMISSION TESTS--
    #     # unauthenticated
    #     response = self.client.post(url, request_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    #     # Admin
    #     self.client.force_authenticate(user=self.admin)
    #     response = self.client.post(url, request_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     # Authenticated
    #     self.client.force_authenticate(user=self.task_unrelated_user)
    #     response = self.client.post(url, request_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     # Is Task instance
    #     task_id = response.data.get('id')
    #     task_instance = get_object_or_404(models.Task, id=task_id)
    #     self.assertTrue(isinstance(task_instance, models.Task))
    #     # Correct owner
    #     self.assertEqual(
    #         task_instance.owner, self.task_unrelated_user.profile
    #     )

    #     # --FIELD TESTS--
    #     # convert dates to expected serialized date format
    #     completed_at = request_data.get('completed_at').strftime(
    #         '%Y-%m-%dT%H:%M:%S.%fZ'
    #     )
    #     due_date = request_data.get(
    #         'due_date').strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    #     # Expected data is an extension of request data
    #     expected_fields = {
    #         'id': task_instance.id,
    #         'owner': response.wsgi_request.user.email,
    #         'title': request_data.get('title'),
    #         'description': request_data.get('description'),
    #         'due_date': due_date,
    #         'completed_at': completed_at,
    #         'category': request_data.get('category'),
    #         'priority': request_data.get('priority'),
    #         'status': request_data.get('status'),
    #         'team_members': []
    #     }

    #     # Serialize the created Task instance
    #     actual_fields = serializers.TaskSerializer(
    #         instance=task_instance
    #     ).data

    #     # both created_at fields are set to date() to succeed in
    #     # comparisson otherwise millisecond difference fails test
    #     created_at = actual_fields.pop('created_at', None)
    #     created_at_date_format = datetime.strptime(
    #         created_at, '%Y-%m-%dT%H:%M:%S.%fZ'
    #     ).date()

    #     actual_fields['created_at'] = created_at_date_format
    #     expected_fields['created_at'] = timezone.now().date()

    #     self.assertEqual(actual_fields, expected_fields)
