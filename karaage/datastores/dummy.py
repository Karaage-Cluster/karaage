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

""" LDAP datastore. """

import logging

import karaage.common.trace as trace
from karaage.datastores import base


logger = logging.getLogger(__name__)


class DataStore(base.DataStore):
    """ LDAP Account and group datastore. """

    def __init__(self, config):
        super(DataStore, self).__init__(config)
        self.value = config.get('value', 'Metrotrains forgot')

    def get_account_details(self, account):
        """ Get the account details. """
        return {
            'type': 'account',
            'answer': '42',
            'value': self.value,
        }

    def account_exists(self, username):
        """ Does the account exist? """
        return False

    def get_group_details(self, group):
        """ Get the group details. """
        return {
            'type': 'group',
            'answer': '42',
            'value': self.value,
        }

    def get_project_details(self, project):
        """ Get project's details. """
        return {
            'type': 'project',
            'answer': '42',
            'value': self.value,
        }

    def get_institute_details(self, institute):
        """ Get institute's details. """
        return {
            'type': 'institute',
            'answer': '42',
            'value': self.value,
        }


trace.attach(trace.trace(logger), DataStore)
