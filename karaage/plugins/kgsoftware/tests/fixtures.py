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

try:
    from factory.django import DjangoModelFactory
    import factory
except ImportError:
    raise ImportError(
        "factory_boy is required, "
        "either install from a package or using \'pip install -e .[tests]\'")

from karaage.tests.fixtures import fuzzy_lower_text, GroupFactory

from ..models import Software


class SoftwareFactory(DjangoModelFactory):
    name = fuzzy_lower_text(prefix='soft-')
    group = factory.SubFactory(GroupFactory)

    class Meta:
        model = Software
        django_get_or_create = ('name',)
