from django.core.management.base import BaseCommand

from no import get_reason


class Command(BaseCommand):
    help = "Print a reason to say no."

    def handle(self, *args, **options):
        self.stdout.write(get_reason())
