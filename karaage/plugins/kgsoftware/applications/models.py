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

import six
import datetime

from django.db import models


from ..models import SoftwareLicense, SoftwareLicenseAgreement

from karaage.plugins.kgapplications.models \
    import Application, ApplicationManager


class SoftwareApplication(Application):
    type = "software"
    software_license = models.ForeignKey(SoftwareLicense)

    objects = ApplicationManager()

    class Meta:
        db_table = 'applications_softwareapplication'

    def info(self):
        return six.u("access software %s") % self.software_license.software

    def check_valid(self):
        errors = super(SoftwareApplication, self).check_valid()

        if self.content_type.model != 'person':
            errors.append("Applicant not already registered person.")

        return errors

    def approve(self, approved_by):
        created_person = super(SoftwareApplication, self).approve(approved_by)

        try:
            sla = SoftwareLicenseAgreement.objects.get(
                person=self.applicant,
                license=self.software_license,
            )
        except SoftwareLicenseAgreement.DoesNotExist:
            sla = SoftwareLicenseAgreement()
            sla.person = self.applicant
            sla.license = self.software_license
            sla.date = datetime.datetime.today()
            sla.save()

        if self.software_license.software.group is not None:
            self.software_license.software.group.add_person(self.applicant)
        return created_person
