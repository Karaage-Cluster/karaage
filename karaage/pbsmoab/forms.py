from django import forms

from models import ProjectChunk


class ProjectChunkForm(forms.ModelForm):

    class Meta:
        model = ProjectChunk
        exclude = ('project',)
