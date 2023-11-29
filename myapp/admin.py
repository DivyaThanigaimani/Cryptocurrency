from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import Country, Province, Region, Location, PaymentHistory, Subscription, ContactMessage, GlossaryTerm, \
    Payment

admin.site.register(Subscription)
admin.site.register(ContactMessage)
admin.site.register(PaymentHistory)
admin.site.register(GlossaryTerm)
admin.site.register(Payment)
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name']  # Adjust the fields you want to display in the admin list view


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['name', 'country']  # Adjust the fields you want to display in the admin list view

