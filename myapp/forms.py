
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from django import forms

# Contact Us imports
from .models import ContactMessage


# Subscribe imports
from django.forms.widgets import PasswordInput, TextInput
from django import forms
from .models import Subscription

from myapp.models import Country, Province, Region, Location
from django import forms
from .models import GlossaryTerm


# - Create/Register a user (Model Form)

class CreateUserForm(UserCreationForm):

    class Meta:

        model = User
        fields = ['username', 'email', 'password1', 'password2']


# - Authenticate a user (Model Form)

class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())


class ExchangeForm(forms.Form):
    country = forms.ModelChoiceField(queryset=Country.objects.all())
    province = forms.ModelChoiceField(queryset=Province.objects.all())
    region = forms.ModelChoiceField(queryset=Region.objects.all())
    location = forms.ModelChoiceField(queryset=Location.objects.all())
    enter_amount = forms.DecimalField()
# Subscribe form
class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
        }


#Contact Us form
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }


class GlossaryTermForm(forms.ModelForm):
    class Meta:
        model = GlossaryTerm
        fields = ['term', 'definition']

        widgets = {
            'definition': forms.Textarea(attrs={'rows': 5}),
        }