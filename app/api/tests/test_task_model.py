from rest_framework.test import APITestCase, APIRequestFactory
from api import models, serializers
from rest_framework import status
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
        self.task_unrelated_user = User.objects.create(user_data, profile_data)

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

    def test_serializer_update(self):
        """
        Tests if the TaskSerializer has write_only true on

        - owner
        - created_at
        - team_members.

        Also checks for successful updating in general.
        """

        category_update = models.Category.objects.create(
            name='Information Technology',
            description='''A domain specialized in the area of information
                         technology'''
        )
        priority_update = models.Priority.objects.create(
            caption='Low Priority'
        )
        status_update = models.Status.objects.create(
            caption='In Completed',
            description='Indicates that a task is completed.'
        )
        data = {
            'title': 'Updated Task Title',
            'description': 'Updated task description.',
            'due_date': timezone.now() + timezone.timedelta(days=5),
            'completed_at': timezone.now() + timezone.timedelta(days=7),
            'category': category_update.name,
            'priority': priority_update.caption,
            'status': status_update.caption,
        }

        # Preparing dates to be compared with serializer dates
        due_date = data.get('due_date').strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ'
        )
        completed_at = data.get('completed_at').strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ'
        )
        created_at = self.task.created_at.strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ'
        )
        expected_data = {
            'id': self.task.id,
            'title': data.get('title'),
            'description': data.get('description'),
            'due_date': due_date,
            'created_at': created_at,
            'completed_at': completed_at,
            'category': category_update.name,
            'priority': priority_update.caption,
            'status': status_update.caption,
            'owner': self.owner.email,
            'team_members': [self.team_member.email],
        }

        serializer = serializers.TaskSerializer(
            instance=self.task,
            data=data,
            partial=True
        )

        # Valid data
        self.assertTrue(serializer.is_valid(raise_exception=True))
        # Is Task instance
        updated_task = serializer.save()
        self.assertTrue(isinstance(updated_task, models.Task))
        # Fields correctly updated
        updated_data = serializers.TaskSerializer(instance=updated_task).data
        self.assertEqual(updated_data, expected_data)

        # read_only fields
        fields = serializer.fields
        read_only_fields = ['created_at', 'owner', 'id', 'team_members']
        for field in fields:
            if field in read_only_fields:
                self.assertTrue(fields.get(field).read_only)

            else:
                self.assertFalse(fields.get(field).read_only)

    def test_serializer_create(self):
        """
        Tests if the TaskSerializer correctly creates Tasks.
        """

        new_category = models.Category.objects.create(
            name='Information Technology',
            description='''A domain specialized in the area of information
                         technology'''
        )
        new_priority = models.Priority.objects.create(
            caption='Low Priority'
        )
        new_update = models.Status.objects.create(
            caption='In Completed',
            description='Indicates that a task is completed.'
        )
        data = {
            'owner': self.owner,
            'title': 'New Task Title',
            'description': 'New task description.',
            'due_date': timezone.now() + timezone.timedelta(days=5),
            'completed_at': timezone.now() + timezone.timedelta(days=7),
            'category': new_category.name,
            'priority': new_priority.caption,
            'status': new_update.caption
        }

        # Preparing dates to be compared with serializer dates
        due_date = data.get('due_date').strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ'
        )
        completed_at = data.get('completed_at').strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ'
        )
        created_at = self.task.created_at.strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ'
        )
        expected_data = {
            'id': self.task.id,
            'title': data.get('title'),
            'description': data.get('description'),
            'due_date': due_date,
            'created_at': created_at,
            'completed_at': completed_at,
            'category': new_category.name,
            'priority': new_priority.caption,
            'status': new_update.caption,
            'owner': self.owner.email,
            'team_members': [self.team_member.email],
        }

        serializer = serializers.TaskSerializer(
            instance=self.task,
            data=data,
            partial=True
        )

        # Valid data
        self.assertTrue(serializer.is_valid(raise_exception=True))
        # Is Task instance
        updated_task = serializer.save()
        self.assertTrue(isinstance(updated_task, models.Task))
        # Fields correctly updated
        updated_data = serializers.TaskSerializer(instance=updated_task).data
        self.assertEqual(updated_data, expected_data)

        # read_only fields
        fields = serializer.fields
        read_only_fields = ['created_at', 'owner', 'id', 'team_members']
        for field in fields:
            if field in read_only_fields:
                self.assertTrue(fields.get(field).read_only)

            else:
                self.assertFalse(fields.get(field).read_only)
