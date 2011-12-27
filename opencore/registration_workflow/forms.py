from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _

from opencore.contact_manager.forms import EmailContactForm

class RegistrationForm(forms.Form):
    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                widget=forms.TextInput(),
                                label=_("Username"),
                                error_messages={
            'invalid': _("This value must contain only letters, numbers and underscores.")})
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(maxlength=75)),
                             label=_("E-mail"))
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                label=_("Password (again)"))
    
    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_email(self):
        email_form = EmailContactForm(data={'email': self.cleaned_data['email']})
        if not email_form.is_valid():
            raise forms.ValidationError(email_form.errors['email'])
        self.email_form = email_form
        return self.cleaned_data['email']

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data

    def save(self):
        username, email, password = (self.cleaned_data['username'], self.cleaned_data['email'],
                                     self.cleaned_data['password1'])
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()

        new_contact = self.email_form.save(new_user)

        self.contact = new_contact
        self.profile = self.email_form.profile

        return new_user


import random
def random_name():
    return "".join(random.choice("abcdefghijklmnopqrxtuvwxyz"
                                 "ABCDEFGHIJKLMNOPQRXTUVWXYZ"
                                 "1234567890@.+-_") for i in range(30))

class TemporaryAccountFactory(object):
    def __init__(self, email):
        self.email = email

    def registration_form(self):
        registration_form = {'username': random_name(),
                             'email': self.email,
                             'password1': random_name()}
        registration_form['password2'] = registration_form['password1']
        registration_form = RegistrationForm(data=registration_form)
        assert registration_form.is_valid()
        return registration_form

    def create_temporary_user(self, registration_form):
        new_user = registration_form.save()
        new_user.set_unusable_password()
        new_user.save()
        return new_user
