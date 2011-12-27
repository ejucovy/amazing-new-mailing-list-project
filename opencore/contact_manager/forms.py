from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _

from main.models import EmailContact
from opencore.contact_manager.models import RegistrationProfile

class EmailContactForm(forms.ModelForm):
    class Meta:
        model = EmailContact
        exclude = ("user", "confirmed")

    def save(self, user):
        contact = forms.ModelForm.save(self, commit=False)
        contact.user = user
        contact.save()

        profile = RegistrationProfile.objects.create_profile(contact)
        self.profile = profile

        return contact
