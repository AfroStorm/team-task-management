from rest_framework.test import APITestCase, APIRequestFactory
from api import models
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class TestTaskResourceModel(APITestCase):
    """
    Tests related to the TaskResource Model.
    """

    def setUp(self) -> None:
        """
        Necessary models for the creation of a TaskResource instance.
        """

        # Foreign key Category Instance for task/position instance
        name = 'Human Resource'
        description = '''A domain specialized in the area of employee
                         recruitment and relationship'''

        self.category_instance = models.Category.objects.create(
            name=name,
            description=description
        )

        # Foreign key Position Instance for userprofile instance
        title = 'Human Resource Specialist'
        description = '''A Position specialized in the area of employee
                         recruitment and relationship'''
        is_task_manager = True
        category = self.category_instance

        self.position_instance = models.Position.objects.create(
            title=title,
            description=description,
            is_task_manager=is_task_manager,
            category=category
        )

        # Foreign key Priority instance for task instance
        caption = 'High Priority'

        self.priority_instance = models.Priority.objects.create(
            caption=caption)

        # Foreign key Status instance for task instance
        caption = 'In Progress'
        description = 'Indicates that a task is stillin progress.'

        self.status_instance = models.Status.objects.create(
            caption=caption,
            description=description
        )

        # Foreign key CostumUser Instance
        # UserProfile gets created for each CustomUser through
        # CustomUserManager

        # User instance as owner for task instance
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
        self.userprofile1 = user.profile

        # User instance as team_member for task.team_members
        email = 'tinaturner@gmail.com'
        password = 'blabla123.'
        first_name = 'Tina'
        last_name = 'Turner'
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
        self.userprofile2 = user.profile

        # Task instance for taskresource instance
        title = 'New Task Instance'
        description = 'A new task created for testing'
        due_date = timezone.now() + timezone.timedelta(days=3)
        # created_at = auto_now_add
        completed_at = timezone.now() + timezone.timedelta(days=1)
        category = self.category_instance
        priority = self.priority_instance
        status = self.status_instance
        owner = self.userprofile1
        team_member = self.userprofile2

        task = models.Task.objects.create(
            title=title,
            description=description,
            due_date=due_date,
            completed_at=completed_at,
            category=category,
            priority=priority,
            status=status,
            owner=owner
        )
        task.team_members.add(team_member)
        self.task = task

        return super().setUp()

    def test_create_task_resource_model(self):
        """
        Tests the creation of a TaskResource instance.
        """

        source_name = '''Improvement For Relationships in The Human Resource
                         Department'''
        description = '''This is an article about how to improve your hands on
                         abilities while negotiating the salary of your
                         employee.'''
        resource_link = 'https://www.example.com/random-page'
        task = self.task

        task_resource = models.TaskResource.objects.create(
            source_name=source_name,
            description=description,
            resource_link=resource_link,
            task=task
        )

        # Source_name correct
        self.assertEqual(task_resource.source_name, source_name)
        # Description correct
        self.assertEqual(task_resource.description, description)
        # Resource_link correct
        self.assertEqual(task_resource.resource_link, resource_link)
        # Task correct
        self.assertIsNotNone(task_resource.task)
        self.assertEqual(task_resource.task, task)
        # Correct str representation
        expected_string = f'ID: {task_resource.id} Title: {source_name}'
        actual_string = str(task_resource)
        self.assertEqual(actual_string, expected_string)
