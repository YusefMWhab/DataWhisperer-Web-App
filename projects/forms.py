from django import forms
from .models import Project


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class ProjectForm(forms.ModelForm):
    project_files = forms.CharField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'multiple': True,
            'type': 'file',
            'accept': '.xlsx, .xls, .csv, .mtt'
        }),
        required=False,
        label="Project Documents"
    )

    class Meta:
        model = Project
        fields = ['name', 'project_type', 'field_manager', 'is_completed']