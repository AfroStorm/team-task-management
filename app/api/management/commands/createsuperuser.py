# Custom management command
from django.core.management.base import BaseCommand
from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth import get_user_model


class Command(createsuperuser):
    help = 'Create a superuser with additional data'

    def handle(self, *args, **options):
        email = input('Enter email: ')
        password = input('Enter password: ')
        first_name = input('Enter first name: ')
        last_name = input('Enter last name: ')
        position = input('Enter position: ')

        # Additional data for UserProfile
        profile_data = {
            'first_name': first_name,
            'last_name': last_name,
            'position': position,
        }

        user_data = {
            'email': email,
            'password': password,
        }

        User = get_user_model()
        User.objects.create_superuser(user_data, profile_data)

        self.stdout.write(self.style.SUCCESS(
            'Superuser created successfully'
        ))
