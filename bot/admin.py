from django.contrib import admin
from .models import *


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'price')
    search_fields = ['name', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user_name',
                    'user_phone',
                    'bouquet')
    search_fields = ('user_phone',
                     'bouquet',
                     'delivery_date')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name']
