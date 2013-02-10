from django import forms
from django.contrib.auth.models import User
from django.forms.widgets       import Input
from django.utils.translation   import ugettext_lazy as _

from registration.forms import RegistrationFormUniqueEmail


class CustomEmailInput(Input):
    """Provides the non-existent `type="email"` HTML5 input.

    Subclasses the Input class and uses `input_type = "email"`.
    """
    input_type = "email"


class CustomRegistrationForm(RegistrationFormUniqueEmail):
    """Extends a django-registration form."""
    attrs_dict = {
        'class':    'required',
        'required': 'required'
    }
    username = forms.CharField(max_length=30,
                               widget=forms.TextInput(
                                   attrs=attrs_dict),  # add autofocus
                               label=_("Username"))

    email = forms.EmailField(
        widget=CustomEmailInput(
            attrs=dict(
                attrs_dict,
                maxlength=75)),
        label=_("E-mail"))

    def clean_email(self):
        """Validate that the supplied e-mail address is unique for the
        site.
        """
        error_message = "This email address is already in use. \
                         Please enter a unique one."

        if "+" in self.cleaned_data['email']:
            raise forms.ValidationError(_(
                "Sorry, we currently do not support +filters in e-mail addresses."))
        elif User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_(error_message))
        # # If the address is of the type name+filter@example.com
        # elif "+" in self.cleaned_data['email'] and User.objects.filter(
        #     # Search for e-mail that begins with name+, ends with @example.com
        #     email__startswith=self.cleaned_data['email'].split("+")[0],
        #     email__endswith='@'+self.cleaned_data['email'].split("@")[1]):
        #     raise forms.ValidationError(_(error_message))

    def clean(self):
        """Verifiy that the values entered into the two password fields
        match.

        Note that an error here will end up in `non_field_errors()`,
        because it doesn't apply to a single field.
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("Your two passwords did not match."))
        return self.cleaned_data
