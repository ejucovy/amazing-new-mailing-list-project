from django.db import models
from opencore import listeners

PROJECT_ROLES = (
    ("ProjectAdmin", "Project Admin"),
    ("ProjectMember", "Project Member"),
    )
PROJECT_POLICIES = (
    ("policy_medium", "Medium"),
    ("policy_closed", "Closed"),
    ("policy_open", "Open"),
    )

class Project(models.Model):
    slug = models.CharField(max_length=100, unique=True)
    policy = models.CharField(choices=PROJECT_POLICIES, db_index=True)

    def members(self):
        return ProjectMember.objects.filter(project=self)

    def viewable(self, request):
        if request.user.is_superuser:
            return True
        if self.policy in ("policy_medium", "policy_open"):
            return True
        if ProjectMember.objects.exists(user=request.user, project=self):
            return True
        return False

    def manageable(self, request):
        if request.user.is_superuser:
            return True
        try:
            membership = ProjectMember.objects.get(user=request.user, project=self)
        except ProjectMember.DoesNotExist:
            return False
        if membership.role == "ProjectAdmin":
            return True
        return False

class ProjectMember(models.Model):
    user = models.ForeignKey("auth.User")
    project = models.ForeignKey(Project)
    role = models.CharField(choices=PROJECT_ROLES, db_index=True)
