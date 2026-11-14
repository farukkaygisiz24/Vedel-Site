from django.conf import settings
from django.core.management.base import BaseCommand

from accounts.digest import field_digest


class Command(BaseCommand):
    help = "Evening field digest: 'Yarın N işiniz var' to each technician (run ~19:00)."

    def handle(self, *args, **options):
        settings.PUSH_SYNC = True
        sent = field_digest()
        self.stdout.write(f'digest: {sent} bildirim')
