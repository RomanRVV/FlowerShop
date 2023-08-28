from django.contrib import admin
from .models import *


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'price')
    search_fields = ['name', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['bouquet']
    search_fields = ('bouquet',
                     'delivery_date')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_id',
                    'client_name')


@admin.register(Flowers)
class FlowersAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'shorten_link', 'place_of_use', 'clicks_count')

    def clicks_count(self, instance):
        return instance.clicks
