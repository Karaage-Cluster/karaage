# Copyright 2014 The University of Melbourne
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

import datetime

from django.conf import settings
from django.contrib.auth.hashers import make_password
try:
    from factory.django import DjangoModelFactory
    from factory.fuzzy import FuzzyText, FuzzyChoice
    import factory
except ImportError:
    raise ImportError("factory_boy is required, either install from a package or using \'pip install -e .[tests]\'")

from karaage.projects.utils import add_user_to_project
import karaage.institutes.models
import karaage.machines.models
import karaage.people.models
import karaage.projects.models


class InstituteFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.institutes.models.Institute
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)

    name = FuzzyText(prefix='inst-')


class PersonFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.people.models.Person
    FACTORY_DJANGO_GET_OR_CREATE = ('username',)

    username = FuzzyText(prefix='user-', chars='abcdefghijklmnopqrstuvwxyz')
    password = make_password('test')
    full_name = factory.LazyAttribute(lambda a: a.username.title()[:50])
    short_name = factory.LazyAttribute(lambda a: a.username.title()[:30])
    email = factory.LazyAttribute(
        lambda a: '{0}@example.com'.format(a.username[:62]).lower())
    institute = factory.SubFactory(InstituteFactory)


class ProjectFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.projects.models.Project
    FACTORY_DJANGO_GET_OR_CREATE = ('pid',)

    pid = FuzzyText(prefix='proj-')
    name = factory.LazyAttribute(lambda a: a.pid.title())
    institute = factory.SubFactory(InstituteFactory)
    is_approved = True
    approved_by = factory.SubFactory(PersonFactory)
    is_active = True


class MachineCategoryFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.machines.models.MachineCategory
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)

    name = FuzzyText(prefix='mc-')
    datastore = 'dummy'


class ProjectQuotaFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.projects.models.ProjectQuota
    FACTORY_DJANGO_GET_OR_CREATE = ('project', 'machine_category')

    project = factory.SubFactory(ProjectFactory)
    machine_category = factory.SubFactory(MachineCategoryFactory)


class AccountFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.machines.models.Account
    FACTORY_DJANGO_GET_OR_CREATE = ('person', 'username', 'machine_category')

    username = FuzzyText(prefix='account-')
    foreign_id = FuzzyText()
    person = factory.SubFactory(PersonFactory)
    machine_category = factory.SubFactory(MachineCategoryFactory)
    date_created = factory.LazyAttribute(lambda a: datetime.datetime.today())
    default_project = factory.SubFactory(ProjectFactory)
    shell = FuzzyChoice(settings.SHELLS)


def simple_account(machine_category=None):
    if not machine_category:
        machine_category = MachineCategoryFactory()
    project = ProjectFactory()
    account = AccountFactory(machine_category=machine_category,
                             default_project=project)
    ProjectQuotaFactory(project=project,
                        machine_category=machine_category)
    add_user_to_project(account.person, project)
    return account
