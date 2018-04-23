from django import forms
from .models import Product
from django_google_maps.widgets import GoogleMapsAddressWidget


class GoogleMapForm(forms.ModelForm):

    class Meta(object):
        model = Product
        fields = ['address', 'geolocation']
        widgets = {
            "address": GoogleMapsAddressWidget(attrs={'disabled': 'disabled'}),
        }
