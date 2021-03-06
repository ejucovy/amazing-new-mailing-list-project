from optparse import make_option
import json
import textwrap
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
import sys
import email

from main import gateway

class Command(BaseCommand):
    def handle(self, *args, **options):
        mailString = sys.stdin.read()
        mailString = mailString.strip()
        msg = email.message_from_string(mailString)
        
        result = gateway.process(msg)

        return
