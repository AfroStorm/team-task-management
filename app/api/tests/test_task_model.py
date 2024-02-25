from rest_framework.test import APITestCase, APIRequestFactory
from api import models
from rest_framework import status
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
        # Foreign key Category Instance
        name = 'Human Resource'
        description = '''A domain specialized in the area of employee
                         recruitment and relationship'''

        self.category_instance = models.Category.objects.create(
            name=name,
            description=description
        )

        # Foreign key Position Instance
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

        # Foreign key Priority instance
        caption = 'High Priority'

        self.priority_instance = models.Priority.objects.create(
            caption=caption)

        # Foreign key Status instance
        caption = 'In Progress'
        description = 'Indicates that a task is stillin progress.'

        self.status_instance = models.Status.objects.create(
            caption=caption,
            description=description
        )

        # Foreign key CostumUser Instance
        # UserProfile gets created for each CustomUser through
        # CustomUserManager

        # First User instance
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

        # Second User instance
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

        return super().setUp()

    def test_create_task_model(self):
        """
        Tests the creation of a Task instance.
        """

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

        # Title correct
        self.assertEqual(task.title, title)
        # Description correct
        self.assertEqual(task.description, description)
        # Due_date correct
        self.assertEqual(task.due_date, due_date)
        # Created correct
        created_at_date = task.created_at.date()
        created_at = timezone.now().date()
        self.assertEqual(created_at_date, created_at)
        # Completed_at correct
        completed_at_date = task.completed_at.date()
        completed_at = completed_at.date()
        self.assertEqual(completed_at_date, completed_at)
        # Category correct
        self.assertEqual(task.category, category)
        # Priority correct
        self.assertEqual(task.priority, priority)
        # Status correct
        self.assertEqual(task.status, status)
        # Owner correct
        self.assertEqual(task.owner, owner)
        # Team member correct
        team_member = self.userprofile2
        task_team_member = task.team_members.get(id=team_member.id)
        self.assertEqual(task_team_member, team_member)
        # Correct str representation
        expected_string = f'ID: {task.id} - Status: {status} - Title: {title}'
        actual_string = str(task)
        self.assertEqual(actual_string, expected_string)
