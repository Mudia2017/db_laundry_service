from enum import unique
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import *


class CreateUserForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(), required=True)
    prefix = forms.CharField(required=True)
    businessName = forms.CharField(required=True)
    mobile = forms.CharField(required=True)
    streetAddress1 = forms.CharField(required=True)
    city = forms.CharField(required=True)
    state = forms.CharField(required=True)
    country = forms.CharField(required=True)
    discoverUs = forms.CharField(required=True)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 
            'password2', 'prefix', 'businessName', 'mobile', 'streetAddress1',
            'city', 'state', 'country', 'discoverUs'
        ]


# A CLASS TO CHECK ALL SERVICE FIELD REQUIREMENT ARE MEANT
class ServiceFormField(ModelForm):
    serviceName = forms.CharField(required=True)
    ironNormal = forms.CharField(required=True)
    ironFast = forms.CharField(required=True)
    laundryNormal = forms.CharField(required=True)
    laundryFast = forms.CharField(required=True)
    laundryIronNormal = forms.CharField(required=True)
    laundryIronFast = forms.CharField(required=True)
    dryWashNormal = forms.CharField(required=True)
    dryWashFast = forms.CharField(required=True)
    stainRemoval = forms.CharField(required=True)
    dryUp = forms.CharField(required=True)
    others = forms.CharField(required=True)
    iconId = forms.CharField(required=True)
    class Meta:
        model = Services
        fields = ['serviceName', 'ironNormal', 'ironFast', 'laundryNormal', 'laundryFast', 'laundryIronNormal', 'laundryIronFast', 'dryWashNormal', 'dryWashFast', 'stainRemoval', 'dryUp', 'others', 'updatedDate', 'updatedBy', 'active', 'iconId']


class UpdateComProfile(ModelForm):
    mobile = forms.CharField(required=True)
    streetAddress1 = forms.CharField(required=True) 
    city = forms.CharField(required=True)
    state = forms.CharField(required=True)
    country = forms.CharField(required=True)
    class Meta:
        model = CompanyRegisterForm
        fields = ['mobile', 'streetAddress1', 'city', 'state', 'country']

