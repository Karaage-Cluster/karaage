"""List installed Karaage apps (plugins)."""
from django.core.management.base import NoArgsCommand
from karaage.conf.process import registered_karaage_apps

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        self.stdout.write('\n'.join(registered_karaage_apps()))
