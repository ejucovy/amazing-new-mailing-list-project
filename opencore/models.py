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
    policy = models.CharField(choices=PROJECT_POLICIES, max_length=100, db_index=True)

    @models.permalink
    def get_absolute_url(self):
        return ("project_home", [self.slug], {})

    def __unicode__(self):
        return u"%s: %s" % (self.slug, self.policy)

    @property
    def featurelets(self):
        return ["listen"]

    def members(self):
        return ProjectMember.objects.filter(project=self)

    def viewable(self, request):
        if request.user.is_superuser:
            return True
        if self.policy in ("policy_medium", "policy_open"):
            return True
        if request.user.is_anonymous():
            return False
        try:
            membership = ProjectMember.objects.get(
                user=request.user, project=self)
        except ProjectMember.DoesNotExist:
            pass
        else:
            return True
        return False

    def manageable(self, request):
        if request.user.is_superuser:
            return True
        if request.user.is_anonymous():
            return False
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
    role = models.CharField(choices=PROJECT_ROLES, max_length=100, db_index=True)

    def __unicode__(self):
        return u": ".join((unicode(self.user), unicode(self.project), self.role))

