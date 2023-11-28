from django import forms
from .models import Country, Province, Region, Location


class ExchangeForm(forms.Form):
    country = forms.ModelChoiceField(queryset=Country.objects.all())
    province = forms.ModelChoiceField(queryset=Province.objects.all())
    region = forms.ModelChoiceField(queryset=Region.objects.all())
    location = forms.ModelChoiceField(queryset=Location.objects.all())
    enter_amount = forms.DecimalField()
