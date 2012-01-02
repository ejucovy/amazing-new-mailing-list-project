from django import forms

from opencore.models import Project, ProjectMember
from main.models import EmailContact

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project

    def save(self, user):
        project = forms.ModelForm.save(self)
        membership = ProjectMember(project=project, user=user, role="ProjectAdmin")
        membership.save()
        return project

class ProjectEditForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['slug']

class TeamForm(forms.Form):

    memberships = forms.ModelMultipleChoiceField(
        queryset=ProjectMember.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        error_messages={'required': "You must select at least one member"})

    MEMBERSHIP_ROLES = (
        ('', '--Set Membership Role--'),
        ('M', 'Manager'),
        ('N', 'Regular Member'),
        ('D', 'Remove from Community'),
        )
    role = forms.ChoiceField(choices=MEMBERSHIP_ROLES)

    def __init__(self, project, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.project = project
        self.fields['memberships'].queryset = ProjectMember.objects.filter(
            project=project)

    def clean(self):
        data = self.cleaned_data
        role = data['role'] if 'role' in data else ''
        memberships = data['memberships'] if 'memberships' in data else []
        if ( (role == 'N' or role == 'D') and
             ProjectMember.objects.filter(
                project=self.project, role="ProjectAdmin").count() == 
             len(memberships.filter(role="ProjectAdmin")) ):
            self._errors['memberships'] = forms.util.ErrorList([
                    "You must leave at least one Project Admin."])
            del self.cleaned_data['memberships']
        return self.cleaned_data

    def save(self):
        role = self.cleaned_data['role']
        memberships = self.cleaned_data['memberships']
        if role == 'M':
            memberships.update(role="ProjectAdmin")
        elif role == 'N':
            memberships.update(role="ProjectMember")
        elif role == 'D':
            memberships.delete()
        else:
            raise NameError("Role option %s does not exist" % role)
        return memberships
