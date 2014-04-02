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
    from factory.fuzzy import FuzzyText, FuzzyChoice, FuzzyDecimal
    import factory
except ImportError:
    raise ImportError(
        "factory_boy is required, "
        "either install from a package or using \'pip install -e .[tests]\'")

from karaage.projects.utils import add_user_to_project
import karaage.applications.models
import karaage.institutes.models
import karaage.machines.models
import karaage.people.models
import karaage.projects.models
import karaage.software.models


def FuzzyLowerText(*args, **kwargs):
    if not 'chars' in kwargs:
        kwargs['chars'] = 'abcdefghijklmnopqrstuvwxyz'
    return FuzzyText(*args, **kwargs)


class GroupFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.people.models.Group
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)
    name = FuzzyLowerText(prefix='group-')


class PersonFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.people.models.Person
    FACTORY_DJANGO_GET_OR_CREATE = ('username',)

    username = FuzzyLowerText(prefix='person-')
    password = make_password('test')
    full_name = factory.LazyAttribute(lambda a: a.username.title()[:50])
    short_name = factory.LazyAttribute(lambda a: a.username.title()[:30])
    email = factory.LazyAttribute(
        lambda a: '{0}@example.com'.format(a.username[:62]).lower())
    institute = factory.LazyAttribute(
        lambda a: InstituteFactory(
            name=FuzzyLowerText(prefix='%s-inst-' % a.username)))


class MachineCategoryFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.machines.models.MachineCategory
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)

    name = FuzzyLowerText(prefix='mc-')
    datastore = 'dummy'


class InstituteFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.institutes.models.Institute
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)

    name = FuzzyLowerText(prefix='inst-')
    group = factory.SubFactory(GroupFactory)


class InstituteQuotaFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.institutes.models.InstituteQuota
    FACTORY_DJANGO_GET_OR_CREATE = ('institute', 'machine_category')

    institute = factory.SubFactory(InstituteFactory)
    machine_category = factory.SubFactory(MachineCategoryFactory)
    quota = FuzzyDecimal(0.0, 999.0)


class ProjectFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.projects.models.Project
    FACTORY_DJANGO_GET_OR_CREATE = ('pid',)

    pid = FuzzyLowerText(prefix='proj-')
    name = factory.LazyAttribute(lambda a: a.pid.title()[:200])
    institute = factory.SubFactory(InstituteFactory)
    is_approved = True
    approved_by = factory.LazyAttribute(
        lambda a: PersonFactory(
            username=FuzzyLowerText(prefix='%s-acc-' % a.pid)))
    is_active = True


class ProjectQuotaFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.projects.models.ProjectQuota
    FACTORY_DJANGO_GET_OR_CREATE = ('project', 'machine_category')

    project = factory.SubFactory(ProjectFactory)
    machine_category = factory.SubFactory(MachineCategoryFactory)


class AccountFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.machines.models.Account
    FACTORY_DJANGO_GET_OR_CREATE = ('person', 'username', 'machine_category')

    username = FuzzyLowerText(prefix='account-')
    foreign_id = FuzzyText()
    person = factory.SubFactory(PersonFactory)
    machine_category = factory.SubFactory(MachineCategoryFactory)
    date_created = factory.LazyAttribute(lambda a: datetime.datetime.today())
    default_project = factory.SubFactory(ProjectFactory)
    shell = FuzzyChoice(settings.SHELLS)


class SoftwareFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.software.models.Software
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)

    name = FuzzyLowerText(prefix='soft-')
    group = factory.SubFactory(GroupFactory)


class ApplicationFactory(DjangoModelFactory):
    FACTORY_FOR = karaage.applications.models.Application

    applicant = factory.SubFactory(PersonFactory)


class ProjectApplicationFactory(ApplicationFactory):
    FACTORY_FOR = karaage.applications.models.ProjectApplication


class NewProjectApplicationFactory(ProjectApplicationFactory):
    name = FuzzyLowerText(prefix='projectapplication-')
    description = FuzzyText()
    institute = factory.SubFactory(InstituteFactory)


class ExistingProjectApplicationFactory(ProjectApplicationFactory):
    project = factory.SubFactory(ProjectFactory)


def simple_account(institute=None, machine_category=None):
    if not machine_category:
        machine_category = MachineCategoryFactory()
    if not institute:
        institute = InstituteFactory()
    person = PersonFactory(institute=institute)
    project = ProjectFactory(pid=FuzzyLowerText(prefix='proj-default-'),
                             institute=institute,
                             approved_by=person)
    account = AccountFactory(machine_category=machine_category,
                             person=person,
                             default_project=project)
    ProjectQuotaFactory(project=project,
                        machine_category=machine_category)
    add_user_to_project(account.person, project)
    return account
