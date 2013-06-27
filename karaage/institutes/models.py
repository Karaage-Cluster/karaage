# Copyright 2007-2010 VPAC
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

from django.db import models
from karaage.people.models import Person, Group
from karaage.institutes.managers import ActiveInstituteManager


class Institute(models.Model):
    name = models.CharField(max_length=100, unique=True)
    delegates = models.ManyToManyField(Person, related_name='delegate', blank=True, null=True, through='InstituteDelegate')
    group = models.ForeignKey(Group)
    saml_entityid = models.CharField(max_length=200, null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()
    active = ActiveInstituteManager()

    class Meta:
        ordering = ['name']
        db_table = 'institute'

    def save(self, *args, **kwargs):
        # set group if not already set
        if self.group_id is None:
            name = str(self.name.lower().replace(' ', ''))
            self.group,_ = Group.objects.get_or_create(name=name)

        # update the datastore
        from karaage.datastores.institutes import save_institute
        save_institute(self)

        # save the object
        super(Institute, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # update the datastore
        from karaage.datastores.institutes import delete_institute
        delete_institute(self)

        # delete the object
        super(Institute, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('kg_institute_detail', [self.id])

    @models.permalink
    def get_usage_url(self):
        return ('kg_usage_institute', [1, self.id])

    def get_usage(self, start, end, machine_category=None):
        from karaage.machines.models import MachineCategory
        if machine_category is None:
            machine_category = MachineCategory.objects.get_default()
        from karaage.util.usage import get_institute_usage
        return get_institute_usage(self, start, end, machine_category)

    def gen_usage_graph(self, start, end, machine_category):
        from karaage.graphs import gen_institute_bar
        gen_institute_bar(self, start, end, machine_category)

    def can_view(self, user):
        if not user.is_authenticated():
            return False

        person = user.get_profile()

        # staff members can view everything
        if person.user.is_staff:
            return True

        if not self.is_active:
            return False

        # Institute delegates==person can view institute
        if person in self.delegates.all():
            return True

        return False


class InstituteDelegate(models.Model):
    person = models.ForeignKey(Person)
    institute = models.ForeignKey(Institute)
    send_email = models.BooleanField()

    class Meta:
        db_table = 'institutedelegate'
