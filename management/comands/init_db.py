from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Initializes the database and applies migrations'

    def handle(self, *args, **kwargs):
        self.stdout.write('Initializing the database and applying migrations...')

        try:
            # Ensure that all migrations are created
            call_command('makemigrations')

            # Apply the migrations
            call_command('migrate')

            self.stdout.write(self.style.SUCCESS('Database initialized and migrations applied successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
