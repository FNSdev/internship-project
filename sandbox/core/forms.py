from django import forms
from core.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'repository', 'description')


class InviteUserForm(forms.Form):
    email = forms.EmailField()
    message = forms.CharField(max_length=150)
