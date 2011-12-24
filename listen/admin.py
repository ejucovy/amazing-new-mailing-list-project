from django.contrib import admin

from listen.models import MailingList
from listen.models import AllowedSender
from listen.models import MailingListPost
from listen.models import LocalRoles
from listen.models import RolePermissions
from listen.models import SubscriptionQueue

admin.site.register(MailingList)
admin.site.register(AllowedSender)
admin.site.register(MailingListPost)
admin.site.register(LocalRoles)
admin.site.register(RolePermissions)
admin.site.register(SubscriptionQueue)
