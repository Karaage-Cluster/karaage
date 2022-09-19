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

from django.conf import settings

from karaage import __version__
from karaage.common import is_admin


def common(request):
    """Set context with common variables."""
    ctx = {
        "AAF_RAPID_CONNECT_ENABLED": settings.AAF_RAPID_CONNECT_ENABLED,
        "org_name": settings.ACCOUNTS_ORG_NAME,
        "accounts_email": settings.ACCOUNTS_EMAIL,
        "is_admin": is_admin(request),
        "kgversion": __version__,
        "VERSION": settings.VERSION,
        "BUILD_DATE": settings.BUILD_DATE,
        "VCS_REF": settings.VCS_REF,
        "SLURM_VER": settings.SLURM_VER,
    }

    return ctx
