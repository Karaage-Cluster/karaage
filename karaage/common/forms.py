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

""" Forms for Karaage use. """

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from karaage.common.models import Comment

class CommentForm(forms.ModelForm):
    """ Comment form. """

    class Meta:
        model = Comment
        fields = [ "comment" ]

    def __init__(self, obj, instance=None, **kwargs):
        self.obj = obj
        if instance is not None:
            assert obj == instance.content_object
        return super(CommentForm, self).__init__(instance=instance, **kwargs)

    def save(self, request):
        comment = self.instance
        if comment.pk is None:
            comment.content_object = self.obj
            comment.user = request.user
            comment.site = Site.objects.get_current()
            comment.valid_rating = 0
            comment.is_public = True
            comment.is_removed = False
        return super(CommentForm, self).save(self)
