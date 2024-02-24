# Custom management command
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from getpass import getpass


class Command(BaseCommand):
    help = 'Create a superuser with additional data'

    def handle(self, *args, **options):
        email = input('Enter email: ')
        while True:
            password = getpass('Enter password: ')
            password_confirm = getpass('Confirm password: ')

            if password == password_confirm:
                break
            else:
                self.stdout.write(self.style.ERROR(
                    'Passwords do not match. Please try again.'))
        first_name = input('Enter first name: ')
        last_name = input('Enter last name: ')

        # Additional data for UserProfile
        profile_data = {
            'first_name': first_name,
            'last_name': last_name,
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
