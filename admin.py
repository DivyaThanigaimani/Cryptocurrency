from django.contrib import admin

# Register your models here.
# admin.py
from django.contrib import admin
from .models import Country, Province, Region, Location


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name']  # Adjust the fields you want to display in the admin list view


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['name', 'country']  # Adjust the fields you want to display in the admin list view


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'province']  # Adjust the fields you want to display in the admin list view


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'region']  # Adjust the fields you want to display in the admin list view
