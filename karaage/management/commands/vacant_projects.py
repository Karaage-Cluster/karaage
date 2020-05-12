import sys

import django.db.transaction
from django.core.management.base import BaseCommand

from karaage.projects.models import Project


class Command(BaseCommand):
    help = "return a list of projects with no currently active users"

    @django.db.transaction.non_atomic_requests
    def handle(self, *args, **options):
        badProjects = 0
        for selectedProject in Project.objects.all():
            members = selectedProject.group.members.all()
            memberCount = 0
            invalidCount = 0
            for person in members:
                if person.is_active and person.login_enabled:
                    memberCount += 1
                else:
                    invalidCount += 1
            if memberCount == 0:
                badProjects += 1
                sys.stdout.write("{}: {} locked users".format(selectedProject.pid, invalidCount))
                sys.stdout.write("\n")
        sys.stdout.write("{} inactive/unpopulated projects\n".format(badProjects))
        sys.stdout.write("Done\n")
