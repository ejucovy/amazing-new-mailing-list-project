import datetime
import random
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _

SHA1_RE = re.compile('^[a-f0-9]{40}$')

from main.models import EmailContact

class RegistrationManager(models.Manager):

    def create_profile(self, contact):
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        username = contact.user.username
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        activation_key = sha_constructor(salt+username).hexdigest()
        return self.create(contact=contact,
                           activation_key=activation_key)
        
    def delete_expired_users(self):
        for profile in self.all():
            if profile.activation_key_expired():
                contact = profile.contact
                if not contact.confirmed:
                    contact.delete()


class RegistrationProfile(models.Model):
    ACTIVATED = u"ALREADY_ACTIVATED"
    
    contact = models.ForeignKey(EmailContact, unique=True, 
                                verbose_name=_('contact'))
    activation_key = models.CharField(_('activation key'), max_length=40)
    
    objects = RegistrationManager()
    
    class Meta:
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')
    
    def __unicode__(self):
        return u"Registration information for %s" % self.contact
    
    def activation_key_expired(self):
        expiration_date = datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS)
        if self.activation_key == self.ACTIVATED:
            return True
        ## TODO
        #if (self.contact.user.date_joined + expiration_date <= 
        #        datetime.datetime.now())
        # return True
    activation_key_expired.boolean = True

    def confirm_contact(self):
        contact = self.contact
        contact.confirmed = True
        contact.save()
        self.activation_key = self.ACTIVATED
        self.save()
        return contact
    
    def render_to_string(self, template_name, extra_context={}):
        context = {
            'activation_key': self.activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': {'domain': settings.SITE_DOMAIN,
                     'name': settings.SITE_NAME},
            'profile': self,
            }
        context.update(extra_context)
        return render_to_string(template_name, context)
