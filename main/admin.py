from django.contrib import admin
from main.models import EmailContact
from main.models import DeferredMessage
from main.models import MailingList
from main.models import AllowedSender
from main.models import MailingListPost
from main.models import LocalRoles
from main.models import RolePermissions

admin.site.register(EmailContact)
admin.site.register(DeferredMessage)
admin.site.register(MailingList)
admin.site.register(AllowedSender)
admin.site.register(MailingListPost)
admin.site.register(LocalRoles)
admin.site.register(RolePermissions)
