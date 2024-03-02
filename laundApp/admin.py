from django.contrib import admin
from . models import *

# Register your models here.


class CompanyRegisterFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'businessName', 'mobile', 'phone', 'streetAddress1', 'streetAddress2', 'city', 'state', 'postal', 'businessId')
    readonly_fields = ('businessId',)


class ServicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'serviceName', 'ironNormal', 'ironFast', 'laundryNormal', 'laundryFast', 'laundryIronNormal', 'laundryIronFast', 'dryWashNormal', 'dryWashFast')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'catName', 'active')


admin.site.register(CompanyRegisterForm, CompanyRegisterFormAdmin),
admin.site.register(Services, ServicesAdmin)
admin.site.register(Category, CategoryAdmin)