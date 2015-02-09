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

import six

from django.test import TestCase

from karaage.projects.forms import ProjectForm
from karaage.tests.fixtures import ProjectFactory


class ProjectFormTestCase(TestCase):

    def setUp(self):
        super(ProjectFormTestCase, self).setUp()
        self.project = ProjectFactory()

    def _valid_form_data(self):
        data = {
            'pid': self.project.pid,
            'name': self.project.name,
            'description': self.project.description,
            'institute': self.project.institute.id,
            'additional_req': self.project.additional_req,
            'start_date': self.project.start_date,
            'end_date': self.project.end_date
        }
        return data

    def test_valid_data(self):
        form_data = self._valid_form_data()
        form_data['name'] = 'test-project'
        form = ProjectForm(data=form_data,
                           instance=self.project)
        self.assertEqual(form.is_valid(), True, form.errors.items())
        form.save()
        self.assertEqual(self.project.name, 'test-project')

    def test_invalid_pid(self):
        form_data = self._valid_form_data()
        form_data['pid'] = '!test-project'
        form = ProjectForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'pid': [six.u(
                    'Project names can only contain letters,'
                    ' numbers and underscores')]
            })
        )
