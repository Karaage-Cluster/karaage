import getpass
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from karaage.people.models import Person

class Command(BaseCommand):
    help = "Change a person's password for Karaage."

    def _get_pass(self, prompt="Password: "):
        p = getpass.getpass(prompt=prompt)
        if not p:
            raise CommandError("aborted")
        return p

    def handle(self, *args, **options):
        if len(args) > 1:
            raise CommandError("need exactly one or zero arguments for username")

        if args:
            username, = args
        else:
            username = getpass.getuser()

        try:
            person = Person.objects.get(username=username)
        except Person.DoesNotExist:
            raise CommandError("person '%s' does not exist" % username)

        self.stdout.write("Changing password for person '%s'\n" % person)

        MAX_TRIES = 3
        count = 0
        p1, p2 = 1, 2  # To make them initially mismatch.
        while p1 != p2 and count < MAX_TRIES:
            p1 = self._get_pass()
            p2 = self._get_pass("Password (again): ")
            if p1 != p2:
                self.stdout.write("Passwords do not match. Please try again.\n")
                count = count + 1

        if count == MAX_TRIES:
            raise CommandError("Aborting password change for user '%s' after %s attempts" % (username, count))

        person.set_password(p1)
        person.save()

        return "Password changed successfully for user '%s'" % person
