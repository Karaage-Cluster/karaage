# Copyright 2014-2015 VPAC
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
import karaage.institutes.models
import karaage.machines.models
import karaage.people.models
import karaage.projects.models


def fuzzy_lower_text(*args, **kwargs):
    if 'chars' not in kwargs:
        kwargs['chars'] = 'abcdefghijklmnopqrstuvwxyz'
    return FuzzyText(*args, **kwargs)


class GroupFactory(DjangoModelFactory):
    name = fuzzy_lower_text(prefix='group-')

    class Meta:
        model = karaage.people.models.Group
        django_get_or_create = ('name',)


class PersonFactory(DjangoModelFactory):
    username = fuzzy_lower_text(prefix='person-')
    password = make_password('test')
    full_name = factory.LazyAttribute(lambda a: a.username.title()[:50])
    short_name = factory.LazyAttribute(lambda a: a.username.title()[:30])
    email = factory.LazyAttribute(
        lambda a: '{0}@example.com'.format(a.username[:62]).lower())
    institute = factory.LazyAttribute(
        lambda a: InstituteFactory(
            name=fuzzy_lower_text(prefix='%s-inst-' % a.username)))

    class Meta:
        model = karaage.people.models.Person
        django_get_or_create = ('username',)


class MachineCategoryFactory(DjangoModelFactory):
    name = fuzzy_lower_text(prefix='mc-')
    datastore = 'dummy'

    class Meta:
        model = karaage.machines.models.MachineCategory
        django_get_or_create = ('name',)


class InstituteFactory(DjangoModelFactory):
    name = fuzzy_lower_text(prefix='inst-')
    group = factory.SubFactory(GroupFactory)

    class Meta:
        model = karaage.institutes.models.Institute
        django_get_or_create = ('name',)


class InstituteQuotaFactory(DjangoModelFactory):
    institute = factory.SubFactory(InstituteFactory)
    machine_category = factory.SubFactory(MachineCategoryFactory)
    quota = FuzzyDecimal(0.0, 999.0)

    class Meta:
        model = karaage.institutes.models.InstituteQuota
        django_get_or_create = ('institute', 'machine_category')


class ProjectFactory(DjangoModelFactory):
    pid = fuzzy_lower_text(prefix='proj-')
    name = factory.LazyAttribute(lambda a: a.pid.title()[:200])
    institute = factory.SubFactory(InstituteFactory)
    is_approved = True
    approved_by = factory.LazyAttribute(
        lambda a: PersonFactory(
            username=fuzzy_lower_text(prefix='%s-acc-' % a.pid)))
    is_active = True

    class Meta:
        model = karaage.projects.models.Project


class ProjectQuotaFactory(DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    machine_category = factory.SubFactory(MachineCategoryFactory)

    class Meta:
        model = karaage.projects.models.ProjectQuota
        django_get_or_create = ('project', 'machine_category')


class AccountFactory(DjangoModelFactory):
    username = fuzzy_lower_text(prefix='account-')
    foreign_id = FuzzyText()
    person = factory.SubFactory(PersonFactory)
    machine_category = factory.SubFactory(MachineCategoryFactory)
    date_created = factory.LazyAttribute(lambda a: datetime.datetime.today())
    default_project = factory.SubFactory(ProjectFactory)
    shell = FuzzyChoice(settings.SHELLS)

    class Meta:
        model = karaage.machines.models.Account
        django_get_or_create = ('person', 'username', 'machine_category')


def simple_account(institute=None, machine_category=None):
    if not machine_category:
        machine_category = MachineCategoryFactory()
    if not institute:
        institute = InstituteFactory()
    person = PersonFactory(institute=institute)
    project = ProjectFactory(pid=fuzzy_lower_text(prefix='proj-default-'),
                             institute=institute,
                             approved_by=person)
    account = AccountFactory(machine_category=machine_category,
                             person=person,
                             default_project=project)
    ProjectQuotaFactory(project=project,
                        machine_category=machine_category)
    add_user_to_project(account.person, project)
    return account
