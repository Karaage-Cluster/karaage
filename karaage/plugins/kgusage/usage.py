# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

"""
Methods for getting usage data
uses a database cache to speed up proccess

"""
import datetime

from .models import (
    InstituteCache,
    MachineCache,
    MachineCategoryCache,
    PersonCache,
    ProjectCache,
)


def get_institute_usage(institute, start, end):
    """Return a tuple of cpu hours and number of jobs for an institute
    for a given period

    Keyword arguments:
    institute --
    start -- start date
    end -- end date
    """
    try:
        cache = InstituteCache.objects.get(
            institute=institute, date=datetime.date.today(),
            start=start, end=end)
        return cache.cpu_time, cache.no_jobs
    except InstituteCache.DoesNotExist:
        return 0, 0


def get_project_usage(project, start, end):
    """Return a tuple of cpu hours and number of jobs for a project
    for a given period

    Keyword arguments:
    project --
    start -- start date
    end -- end date

    """
    try:
        cache = ProjectCache.objects.get(
            project=project, date=datetime.date.today(),
            start=start, end=end)
        return cache.cpu_time, cache.no_jobs
    except ProjectCache.DoesNotExist:
        return 0, 0


def get_person_usage(person, project, start, end):
    """Return a tuple of cpu hours and number of jobs for a person in a
    specific project

    Keyword arguments:
    person --
    project -- The project the usage is from
    start -- start date
    end -- end date
    """
    try:
        cache = PersonCache.objects.get(
            person=person, project=project, date=datetime.date.today(),
            start=start, end=end)
        return cache.cpu_time, cache.no_jobs
    except PersonCache.DoesNotExist:
        return 0, 0


def get_machine_usage(machine, start, end):
    """Return a tuple of cpu hours and number of jobs for a machine
    for a given period

    Keyword arguments:
    machine --
    start -- start date
    end -- end date

    """

    try:
        cache = MachineCache.objects.get(
            machine=machine, date=datetime.date.today(),
            start=start, end=end)
        return cache.cpu_time, cache.no_jobs
    except MachineCache.DoesNotExist:
        return 0, 0


def get_machine_category_usage(start, end):
    """Return a tuple of cpu hours and number of jobs
    for a given period

    Keyword arguments:
    start -- start date
    end -- end date

    """

    cache = MachineCategoryCache.objects.get(
        date=datetime.date.today(),
        start=start, end=end)
    return cache
