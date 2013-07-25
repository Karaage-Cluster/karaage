# Copyright 2007-2013 VPAC
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

""" Common hooks for software datastores. """

from django.conf import settings

_DATASTORES = {}

def _init_datastores():
    """ Initialize all datastores. """
    for name, array in settings.SOFTWARE_DATASTORES.iteritems():
        _DATASTORES[name] = []
        for config in array:
            module = __import__(config['ENGINE'], {}, {}, [''])
            _DATASTORES[name].append(module.SoftwareDataStore(config))

def _get_datastores():
    """ Get the default datastores. """
    name = settings.SOFTWARE_DATASTORE
    return _DATASTORES[name]

def save_software(institute):
    """ An institute has been saved. """
    for datastore in _get_datastores():
        datastore.save_software(institute)

def delete_software(institute):
    """ An institute has been deleted. """
    for datastore in _get_datastores():
        datastore.delete_software(institute)

# Initialize data stores
_init_datastores()
