from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin

# Create your models here.


class CustomUserManager(BaseUserManager):
    """
    Manager for CustomUser model.
    """

    def create(self, user_data, profile_data):
        """
        Creates a user instance with normalized email and hashed
        password together with its userprofile.
        """

        email = user_data.pop('email', None)
        password = user_data.pop('password', None)

        normalized_email = self.normalize_email(email)
        user = self.model(email=normalized_email, **user_data)
        user.set_password(password)
        user.save(self._db)

        profile = UserProfile(owner=user, **profile_data)
        profile.save(self._db)

        return user

    def create_superuser(self, user_data, profile_data):
        """
        Creates a superuser instance with its profile.
        """

        user = self.create(user_data, profile_data)
        user.is_staff = True
        user.is_superuser = True
        user.save(self._db)

        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model which includes a profile.
    """

    email = models.EmailField(max_length=100, unique=True)

    objects = CustomUserManager()

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        """
        Returns a string representation of the user based on its
        email.
        """
        return f'Email: {self.email}'


class Priority(models.Model):
    """
    A tag that shows the priority of a task.

    Fields:
    - caption (CharField): The caption field contains a string
      (e.g., 'High Priority').

    Example:
    ```python
    # Creating a new priority instance
    priority = Priority(caption='High Priority')
    priority.save()

    # Creating a task instance related to the priority
    task = Task(priority=priority, title='Example Task',
    description='Task description', due_date='2024-02-03')
    task.save()
    ```
    """
    caption = models.CharField(max_length=30)

    def __str__(self) -> str:
        """
        Returns a string representation of the priority based on its
        caption.
        """
        return f'{self.caption}'


class Status(models.Model):
    """
    A tag that shows the current status of a task.

    Fields:
    - caption (CharField): The caption field contains a string (e.g., 'In Progress').

    Example:
    ```python
    # Creating a new status instance
    status = Status(caption='In Progress')
    status.save()

    # Creating a task instance related to the status
    task = Task(status=status, title='Example Task', description='Task description', due_date='2024-02-03')
    task.save()
    ```
    """
    caption = models.CharField(max_length=30)
    description = models.TextField()

    def __str__(self) -> str:
        """
        Returns a string representation of the status based on its
        caption.
        """
        return f'{self.caption}'


class Category(models.Model):
    """
    Represents the category of a task.

    Attributes:
        name (str): The name of the category (e.g., 'Information Technology').
        description (str): Further information about the category.

    Example:
    ```python
    # Creating a new category instance
    category = Category(
        name='Information Technology',
        description='Tasks related to Information Technology'
    )
    category.save()
    ```
    """
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=255)

    def __str__(self) -> str:
        """
        Returns a string representation of the model based on its 
        name.
        """
        return f'{self.name}'


class Position(models.Model):
    """
    Represents the position of a user within the system.

    Fields:
    - title (str): The title of the position
      (e.g., 'Human Resource Specialist').
    - description (str): Further information about the position.
    - task_manager (bool): When True, gives the user permission to
      create tasks.
    - category (ForeignKey): Foreign key relationship with the
      Category model as the source.

    Example:
    ```python
    position = UserPosition(
        title='Human Resource Specialist',
        description='Responsible for managing HR tasks',
        task_manager=True,
        category='Information Technology'
    )
    position.save()
    ```
    """

    title = models.CharField(max_length=100)
    description = models.TextField()
    is_task_manager = models.BooleanField(default=False)

    category = models.ForeignKey(
        Category,
        on_delete=models.DO_NOTHING,
        related_name='positions',
    )

    def __str__(self) -> str:
        """Shows the model in a string representation based on its
        title.
        """
        return f'{self.title}'


class UserProfile(models.Model):
    """
    Userprofile for CustomUser Model.
    """

    owner = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='employee'
    )


class Task(models.Model):
    """
    A task with different status options.

    Fields:
    - title (CharField): The title of the task.
    - description (TextField): The description of the task.
    - due_date (DateField): The due date of the task.
    - category (ForeignKey): Foreign key relationship with the
      Category model.
    - priority (ForeignKey): Foreign key relationship with the
      Priority model.
    - status (ForeignKey): Foreign key relationship with the Status
      model.
    - owner (One-To-One): One-To-One relationship with the
      UserProfile model.
    - team_members (Many-To-Many): Many-To-Many relationship with the
      UserProfile model.

    Example:
    ```python
    # Creating a new category instance
    category = Category(name='Development')
    category.save()

    # Creating a new priority instance
    priority = Priority(caption='High Priority')
    priority.save()

    # Creating a new status instance
    status = Status(caption='In Progress')
    status.save()

    # Creating a new user profile instance
    user_profile = UserProfile(owner=user, first_name='John',
    last_name='Doe', phone_number=017833557,
    email='johndoe@gmail.com')
    user_profile.save()

    # Creating a new task instance
    task = Task(title='Example Task', description='Task description',
    due_date='2024-02-03', category=category, priority=priority,
    status=status, owner=user_profile
    task.save()

    # Creating a new task resource instance related to the task
    task_resource = TaskResource(source_name='Example Resource',
    description='Resource description',
    resource_link='https://example.com/resource')
    task_resource.task = task
    task_resource.save()
    ```

    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.DO_NOTHING,
        related_name='category_tasks'
    )
    priority = models.ForeignKey(
        Priority,
        on_delete=models.DO_NOTHING,
        related_name='priority_tasks'
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.DO_NOTHING,
        related_name='status_tasks',
        null=True,
        blank=True
    )

    owner = models.ForeignKey(
        UserProfile,
        on_delete=models.DO_NOTHING,
        related_name='owned_tasks'
    )
    team_members = models.ManyToManyField(
        UserProfile,
        related_name='team_member_tasks',
    )

    def __str__(self) -> str:
        """
        Returns a string representation of the task based on its ID,
        status, and title.
        """
        return f'ID: {self.id} - Status: {self.status} - Title: {self.title}'


class TaskResource(models.Model):
    """
    A Resource of the task (image, document, website link).

    Fields:
    - source_name (CharField): The name of the resource.
    - description (TextField): The description of the resource.
    - resource_link (CharField): The link to the resource.
    - task (ForeignKey): Foreign key relationship with the Task model.

    Example:
    ```python
    # Creating a new task resource instance
    task_resource = TaskResource(source_name='Example Resource',
    description='Resource description',
    resource_link='https://example.com/resource')
    task_resource.save()

    # Creating a new task instance related to the task resource
    task = Task(title='Example Task', description='Task description',
    due_date='2024-02-03')
    task.save()
    task_resource.task = task
    task_resource.save()
    ```

    """
    source_name = models.CharField(max_length=100)
    description = models.TextField()
    resource_link = models.CharField(max_length=500)

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='task_resource'
    )

    def __str__(self) -> str:
        """
        Returns a string representation of the task resource based on
        its ID and source name.
        """
        return f'ID: {self.id} Title: {self.source_name}'
