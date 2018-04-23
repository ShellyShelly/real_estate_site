from cities_light.management.commands import cities_light
import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    currency_type = django_filters.ChoiceFilter(
        choices=Product.CURRENCY_TYPE__CHOICES)
    area_unit_type = django_filters.ChoiceFilter(
        choices=Product.AREA_UNIT_TYPE__CHOICES)
    offer_type = django_filters.ChoiceFilter(
        choices=Product.OFFER_TYPE__CHOICES)
    object_type = django_filters.ChoiceFilter(
        choices=Product.OBJECT_TYPE__CHOICES)
    region = django_filters.ModelChoiceFilter(
        queryset=cities_light.Region.objects.all())

    def __init__(self, *args, **kwargs):
        if not 'queryset' in kwargs:
            kwargs['queryset'] = Product.objects.all()
        super(ProductFilter, self).__init__(*args, **kwargs)
        self.filters['title__icontains'].label = u'Заголовок'
        self.filters['price__gte'].label = u'Ціна Від'
        self.filters['price__lte'].label = u'Ціна До'
        self.filters['currency_type'].label = u'Валюта'
        self.filters['area__gte'].label = u'Площа Від'
        self.filters['area__lte'].label = u'Площа До'
        self.filters['city_detail__icontains'].label = u'Місто'
        self.filters['region_detail__icontains'].label = u'Область'
        self.filters['district_detail__icontains'].label = u'Район'
        self.filters['street_detail__icontains'].label = u'Вулиця'

    class Meta:
        model = Product
        fields = {
            'title': ['icontains'],
            'price': ['gte', 'lte'],
            'area': ['gte', 'lte'],
            'currency_type': [],
            'area_unit_type': [],
            'offer_type': [],
            'object_type': [],
            'city_detail': ['icontains'],
            'region_detail': ['icontains'],
            'district_detail': ['icontains'],
            'street_detail': ['icontains'],
            'region': [],
        }
