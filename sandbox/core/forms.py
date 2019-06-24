from django import forms
from core.models import Project, Task


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'repository', 'description', 'public', 'auto_sync_with_github')


class InviteUserForm(forms.Form):
    email = forms.EmailField()
    message = forms.CharField(max_length=150)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('name', 'description', 'priority', 'status', 'assignees', 'deadline', 'branches')

    deadline = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        ),
        required=False
    )
