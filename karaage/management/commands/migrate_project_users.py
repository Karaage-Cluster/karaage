import sys

import django.db.transaction
import tldap.transaction
from django.core.management.base import BaseCommand

from karaage.projects.models import Project


class Command(BaseCommand):
    help = "Move all project users (except leaders) out of project safely"

    def add_arguments(self, parser):
        parser.add_argument(action="store", dest="Project1", type=str, help="Project to move users from")
        parser.add_argument(
            action="store", dest="Project2", type=str, help="Catchall project for users with no remaining project"
        )

    @django.db.transaction.non_atomic_requests
    @tldap.transaction.commit_on_success
    def handle(self, *args, **options):

        Project1 = options.get("Project1")
        Project2 = options.get("Project2")

        # get list of project members
        # first verify projects exist
        try:
            projectA = Project.objects.get(pid=Project1)
        except Project.DoesNotExist:
            sys.stderr.write("ERROR: Failed to find %s" % Project1)
            sys.exit(1)

        try:
            projectB = Project.objects.get(pid=Project2)
        except Project.DoesNotExist:
            sys.stderr.write("ERROR: Failed to find %s" % Project2)
            sys.exit(1)

        members = projectA.group.members.all()
        leaders = projectA.leaders.all()

        for person in members:
            # determine if the user is a leader of the given project, abort if true.

            if person in leaders:

                # do nothing
                sys.stdout.write("ignoring %s, project leader\n" % person)
            else:

                # determine if the project is the default for any of the user's
                # accounts... but first sort out whether we've got a single
                # case or a list.

                accountlist = person.account_set.all()
                accountlist = accountlist.filter(date_deleted__isnull=True)
                if accountlist.count() == 1:
                    account = person.get_account()
                    if projectA == account.default_project:

                        sys.stdout.write("changing default project for %s to " % person)
                        sys.stdout.write(projectB.pid)
                        sys.stdout.write("\n")
                        # set default project to projectB
                        person.add_group(projectB.group)
                        account.default_project = projectB
                        account.save()
                    # remove user from group
                    sys.stdout.write("removing %s from group " % person)
                    sys.stdout.write(projectA.pid)
                    sys.stdout.write("\n")
                    person.remove_group(projectA.group)
                elif accountlist.count() > 1:
                    # iterate over groups
                    for account in accountlist:
                        if projectA == account.default_project:
                            # set default project to projectB
                            sys.stdout.write("changing default project for %s to " % person)
                            sys.stdout.write(projectB.pid)
                            sys.stdout.write("\n")
                            person.add_group(projectB.group)
                            account.default_project = projectB
                            account.save()
                    sys.stdout.write("removing %s from group " % person)
                    sys.stdout.write(projectA.pid)
                    sys.stdout.write("\n")
                    person.remove_group(projectA.group)
                else:
                    sys.stdout.write("user %s appears to have no active account.. this shouldn't happen")

        sys.stdout.write("Done")
