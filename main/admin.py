from django.contrib import admin

from main.models import EmailContact
from main.models import DeferredMessage

admin.site.register(EmailContact)
admin.site.register(DeferredMessage)
