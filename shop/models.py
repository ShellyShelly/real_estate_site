import os
import requests

from django.db import models
from django.urls import reverse
from django_google_maps import fields as map_fields
from django.dispatch.dispatcher import receiver

from real_estate_site import settings


# Create your models here.
class Product(models.Model):
    title = models.CharField(
        max_length=120,
        verbose_name="Заголовок",
    )
    about = models.TextField(
        blank=True,
        verbose_name="Додаткова інформація",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Дата публікації',
    )

    OBJECT_TYPE__CHOICES = (
        ("land", "Земля"),
        ("object", "Об'єкт нерухомості"),
    )
    object_type = models.CharField(
        max_length=20,
        choices=OBJECT_TYPE__CHOICES,
        verbose_name="Тип об'єкту",
    )

    OFFER_TYPE__CHOICES = (
        ("rent", "Оренда"),
        ("sale", "Продаж"),
    )
    offer_type = models.CharField(
        max_length=20,
        choices=OFFER_TYPE__CHOICES,
        verbose_name='Тип пропозиції',
    )

    price = models.DecimalField(
        max_digits=6,
        decimal_places=0,
        blank=True,
        null=True,
        verbose_name='Ціна',
    )
    CURRENCY_TYPE__CHOICES = (
        ("UAH", "₴"),
        ("USD", "$"),
        ("EUR", "€"),
    )
    currency_type = models.CharField(
        max_length=20,
        choices=CURRENCY_TYPE__CHOICES,
        default=CURRENCY_TYPE__CHOICES[0],
        verbose_name='Грошова одиниця'
    )

    area = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=False,
        null=False,
        verbose_name='Площа')
    AREA_UNIT_TYPE__CHOICES = (
        ("m2", "М²"),
        ("ha", "Га"),
        ("a", "А"),
    )
    area_unit_type = models.CharField(
        max_length=20,
        choices=AREA_UNIT_TYPE__CHOICES,
        default=AREA_UNIT_TYPE__CHOICES[0],
        verbose_name='Величина вимірювання'
    )

    city = models.ForeignKey(
        to='cities_light.City',
        help_text="City Foreign Key",
        on_delete=models.PROTECT,
        verbose_name='Місто',
    )
    region = models.ForeignKey(
        to='cities_light.Region',
        help_text="Region Foreign Key",
        on_delete=models.PROTECT,
        verbose_name='Область',
    )

    city_detail = models.CharField(
        blank=True,
        max_length=120,
        verbose_name='Місто'
    )

    region_detail = models.CharField(
        blank=True,
        max_length=120,
        verbose_name='Область'
    )

    district_detail = models.CharField(
        blank=True,
        max_length=120,
        verbose_name='Район'
    )

    street_detail = models.CharField(
        blank=True,
        max_length=120,
        verbose_name='Вулиця'
    )
    street_number_detail = models.CharField(
        blank=True,
        max_length=20,
        verbose_name='Номер будинку'
    )

    address = map_fields.AddressField(
        max_length=200,
        blank=True,
        verbose_name='Адреса'
    )
    geolocation = map_fields.GeoLocationField(
        max_length=100,
        blank=True,
        verbose_name='Місце на карті',
    )

    def save(self, *args, **kwargs):
        # Use Google's reverse geocoder directly by url
        base = "https://maps.googleapis.com/maps/api/geocode/json?"
        params = "address={address}".format(
            address=self.address,
        )
        key = settings.GOOGLE_MAPS_API_KEY
        languages = "uk"
        url = "{base}{params}&key=%20{key}&language={language}".format(
            base=base,
            params=params,
            key=key,
            language=languages
        )
        while True:
            response = requests.get(url).json()
            if response['status'] == 'OK':
                result = response['results'][0]
                break

        for component in result['address_components']:
            if 'street_number' in component['types']:
                self.street_number_detail = component['long_name']
            if 'route' in component['types']:
                self.street_detail = component['long_name']
            if 'locality' in component['types']:
                self.city_detail = component['long_name']
            if 'administrative_area_level_1' in component['types']:
                self.region_detail = component['long_name']
            if 'administrative_area_level_2' in component['types']:
                self.district_detail = component['long_name']
        self.address = result['formatted_address']
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:ProductDetail', args=[str(self.id)])

    class Meta:
        ordering = ['title', 'pub_date']
        verbose_name = "Об'єкт"
        verbose_name_plural = "Об'єкти"


class Image(models.Model):
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        help_text="Photo Foreign Key",
        verbose_name="Об'єкт",
        related_name="images",
    )
    image = models.ImageField(
        blank=True,
        upload_to='images/shop/%Y/%m/%d',
        verbose_name='Фотографії',
    )


# These two auto-delete files from filesystem when they are unneeded:
@receiver(models.signals.post_delete, sender=Image)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Image` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=Image)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `Image` object is updated
    with new file.
    """
    if not instance.pk:
        return False
    try:
        old_file = Image.objects.get(pk=instance.pk).file
    except Image.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
