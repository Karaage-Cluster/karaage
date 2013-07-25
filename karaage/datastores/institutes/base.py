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

""" Base functionality used by all institute datastores. """

class InstituteDataStore:
    """ Base clase for institute datastores. """

    def __init__(self, config):
        pass

    def save_institute(self, institute):
        """ Institute was saved. """
        raise NotImplementedError

    def delete_institute(self, institute):
        """ Institute was deleted. """
        raise NotImplementedError
