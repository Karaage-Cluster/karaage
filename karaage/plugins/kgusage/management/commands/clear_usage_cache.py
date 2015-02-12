# Copyright 2015 VPAC
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

from django.core.management.base import BaseCommand
import django.db.transaction
import tldap.transaction


class Command(BaseCommand):
    help = "Cleans up usage cache"

    @django.db.transaction.atomic
    @tldap.transaction.commit_on_success
    def handle(self, **options):
        verbose = int(options.get('verbosity'))
        from ... import models
        if verbose > 1:
            print("Clearing project cache")
        models.ProjectCache.objects.all().delete()
        if verbose > 1:
            print("Clearing institute cache")
        models.InstituteCache.objects.all().delete()
        if verbose > 1:
            print("Clearing user cache")
        models.PersonCache.objects.all().delete()
        if verbose > 1:
            print("Clearing machine cache")
        models.MachineCache.objects.all().delete()
        if verbose > 1:
            print("Clearing machine category cache")
        models.MachineCategoryCache.objects.all().delete()
