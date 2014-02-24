# Copyright 2007-2014 VPAC
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

""" Forms for Karaage use. """

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from karaage.common.models import LogEntry, COMMENT

class CommentForm(forms.ModelForm):
    """ Comment form. """

    class Meta:
        model = LogEntry
        fields = [ "change_message" ]

    def __init__(self, obj, instance=None, **kwargs):
        self.obj = obj
        if instance is not None:
            assert instance.action_flag == COMMENT
            assert obj == instance.content_object
        return super(CommentForm, self).__init__(instance=instance, **kwargs)

    def save(self, request):
        log = super(CommentForm, self).save(commit=False)
        log.content_object = self.obj
        log.object_repr = unicode(self.obj)
        log.action_flag = COMMENT
        log.user = request.user
        log.save()
