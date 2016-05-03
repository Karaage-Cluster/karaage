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
from __future__ import absolute_import

import os.path
import logging
import pwd
import grp
import errno


class FileHandler(logging.FileHandler):

    def __init__(self, filename, owner=None, **kwargs):
        if owner:
            if not os.path.exists(filename):
                open(filename, 'a').close()
            uid = pwd.getpwnam(owner[0]).pw_uid
            gid = grp.getgrnam(owner[1]).gr_gid
            try:
                os.chown(filename, uid, gid)
            except OSError as ex:
                if ex.errno != errno.EPERM:
                    raise
        super(FileHandler, self).__init__(filename=filename, **kwargs)
