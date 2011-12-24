from django import forms

from opencore.models import Project, ProjectMember

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project

    def save(self, user):
        project = forms.ModelForm.save(self)
        membership = ProjectMember(project=project, user=user, role="ProjectAdmin")
        membership.save()
        return project
