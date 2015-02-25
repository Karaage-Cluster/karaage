# Copyright 2014-2015 VPAC
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

try:
    from factory.django import DjangoModelFactory
    from factory.fuzzy import FuzzyText
    import factory
except ImportError:
    raise ImportError(
        "factory_boy is required, "
        "either install from a package or using \'pip install -e .[tests]\'")

from karaage.tests.fixtures import FuzzyLowerText, \
    PersonFactory, InstituteFactory, ProjectFactory

from ..models import Application, ProjectApplication


class ApplicationFactory(DjangoModelFactory):
    FACTORY_FOR = Application

    applicant = factory.SubFactory(PersonFactory)


class ProjectApplicationFactory(ApplicationFactory):
    FACTORY_FOR = ProjectApplication


class NewProjectApplicationFactory(ProjectApplicationFactory):
    name = FuzzyLowerText(prefix='projectapplication-')
    description = FuzzyText()
    institute = factory.SubFactory(InstituteFactory)


class ExistingProjectApplicationFactory(ProjectApplicationFactory):
    project = factory.SubFactory(ProjectFactory)
