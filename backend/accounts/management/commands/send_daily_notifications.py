from django.core.management.base import BaseCommand

from accounts.digest import daily


class Command(BaseCommand):
    help = 'Daily bell entries (maintenance coming due) and 90-day notification cleanup (run ~08:00).'

    def handle(self, *args, **options):
        result = daily()
        self.stdout.write(f"bakım: {result['maintenance']} bildirim · silinen: {result['pruned']}")
