from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings

# Create your models here.


class CompanyRegisterForm(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    businessName = models.CharField(max_length=200, default='', unique=True)
    mobile = models.CharField(max_length=15, default='', blank=True)
    phone = models.CharField(max_length=15, default='', blank=True)
    streetAddress1 = models.CharField(max_length=200, default='', blank=True)
    streetAddress2 = models.CharField(max_length=200, default='', blank=True)
    city = models.CharField(max_length=200, default='', blank=True)
    state = models.CharField(max_length=200, default='', blank=True)
    postal = models.CharField(max_length=200, default='', blank=True)
    country = models.CharField(max_length=200, default='', blank=True)
    businessId = models.CharField(max_length=15, default='', blank=True, unique=True)
    discoverUs = models.CharField(max_length=200, blank=True)
    others = models.CharField(max_length=200, default='', blank=True)
    active = models.BooleanField(default=True, null=True, blank=False)
    acctLevel = models.IntegerField(default=1, null=True, blank=True)
    joinDate = models.DateTimeField(auto_now_add=True)
    lastLogin = models.DateTimeField(blank=True, null=True)
    otpConfirm = models.BooleanField(default=False, blank=False)
    termsCondition = models.BooleanField(default=False, null=True, blank=False)

    def __str__(self):
        return self.businessName

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

    
class Category(models.Model):
    comProfileField = models.ForeignKey(CompanyRegisterForm, on_delete=models.SET_NULL, null=True, blank=True)
    catName = models.CharField(max_length=200, default='', blank=True)
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(blank=True, null=True)
    updatedBy = models.CharField(max_length=200, default='', blank=True)
    active = models.BooleanField(default=True, null=True, blank=False)

    def __str__(self):
        return self.catName


class Services(models.Model):
    comProfileField = models.ForeignKey(CompanyRegisterForm, on_delete=models.SET_NULL, null=True)
    categoryId = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    serviceName = models.CharField(max_length=200, default='', blank=True)
    ironNormal = models.CharField(max_length=200, default='', blank=True)
    ironFast = models.CharField(max_length=200, default='', blank=True)
    laundryNormal = models.CharField(max_length=200, default='', blank=True)
    laundryFast = models.CharField(max_length=200, default='', blank=True)
    laundryIronNormal = models.CharField(max_length=200, default='', blank=True)
    laundryIronFast = models.CharField(max_length=200, default='', blank=True)
    dryWashNormal = models.CharField(max_length=200, default='', blank=True)
    dryWashFast = models.CharField(max_length=200, default='', blank=True)
    stainRemoval = models.CharField(max_length=200, default='', blank=True)
    dryUp = models.CharField(max_length=200, default='', blank=True)
    others = models.CharField(max_length=200, default='', blank=True)
    iconId = models.CharField(max_length=60, default='', blank=True)
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(blank=True, null=True)
    updatedBy = models.CharField(max_length=200, default='', blank=True)
    createdBy = models.CharField(max_length=200, default='', blank=True)
    active = models.BooleanField(default=True, null=True, blank=False)

    def __str__(self):
        return self.serviceName