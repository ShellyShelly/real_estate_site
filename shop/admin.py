from django.contrib import admin
from django.contrib.auth.models import Group

from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields

from .models import Product, Image


# Register your models here.
class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    view_on_site = True
    inlines = (
        ImageInline,
    )
    ordering = (
        'title',
        'pub_date',
    )
    list_display = (
        'title',
        'pub_date',
    )
    search_fields = (
        'title',
    )
    readonly_fields = (
        'pub_date',
        'city_detail',
        'region_detail',
        'street_detail',
        'district_detail',
        'street_number_detail',
    )
    autocomplete_fields = (
        'city',
        'region',
    )
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},
    }
    fieldsets = (
        ('Основне', {
            'fields': ('title', 'price', 'currency_type', 'area', 'area_unit_type', 'object_type', 'offer_type', )
        }),
        ('Адреса', {
            'fields': ('address', 'geolocation', )
        }),
        ('Автозаповнення', {
            'fields': ('region_detail', 'district_detail', 'city_detail', 'street_detail', 'street_number_detail', )
        }),
        ('Додатково', {
            'fields': ('city', 'region', 'about', 'pub_date', )
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.save()

        for afile in request.FILES.getlist('photos_multiple'):
            obj.images.create(image=afile)


admin.site.register(Product, ProductAdmin)
admin.site.unregister(Group)
