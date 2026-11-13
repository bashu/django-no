from typing import Any

from django.core.management.base import BaseCommand

from no import get_reason


class Command(BaseCommand):
    help = "Print a reason to say no."

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write(get_reason())
