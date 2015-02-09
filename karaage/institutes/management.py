# Copyright 2010-2011, 2014-2015 VPAC
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

"""
Creates the default Site object.
"""

# Shouldn't really be here but need somewhere that isn't managed by south and
# will execute.
from django.db.models import signals
from django.contrib.sites.models import Site
from django.contrib.sites import models as site_app


def create_secondary_site(app, created_models, verbosity, db, **kwargs):
    if Site in created_models:
        if verbosity >= 2:
            print("Creating registration Site object")
        s = Site(domain="example.com", name="registration")
        s.save(using=db)
    Site.objects.clear_cache()

signals.post_syncdb.connect(create_secondary_site, sender=site_app)
