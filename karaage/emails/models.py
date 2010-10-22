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

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, help_text="Do not change")
    description = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    body = models.TextField(help_text="DONT PAY MUCH ATTENTION TO THIS - Variables available:<br/>{{ requester }} - person requesting<br/>{{ reciever }} - person receiving the email<br/>{{ project }} - project<br/>{{ site }} - link to site")
    
    class Meta:
        permissions = (
            ("send_email", "Can send email"),
        )

    def __unicode__(self):
        return self.name
    
