from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUserManager(models.Manager):
    """
    Manager for CustomUser model.
    """

    def create(self, **kwargs):

        return super().create(**kwargs)


class CustomUser(AbstractUser):
    """
    Custom user model which includes a profile.
    """

    email = models.EmailField(max_length=100, unique=True)

    objects = CustomUserManager()

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAMEFIELD = 'email'

    def __str__(self) -> str:
        """
        Returns a string representation of the user based on its email.
        """
        return f'Email: {self.email}'


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
        """Returns a string representation of the model based on its name."""
        return f'{self.name}'


class Position(models.Model):
    """
    Represents the position of a user within the system.

    Fields:
    - title (str): The title of the position (e.g., 'Human Resource Specialist').
    - description (str): Further information about the position.
    - task_manager (bool): When True, gives the user permission to create tasks.
    - category (ForeignKey): Foreign key relationship with the Category model as the source.

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
    first_name = models.CharField(mx_length=100)
    last_name = models.CharField(mx_length=100)
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='employee'
    )
