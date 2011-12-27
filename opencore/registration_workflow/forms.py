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
