from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
        verbose_name='Користувач',
    )
    is_online = models.BooleanField(
        default=False,
        verbose_name='Онлайн',
    )
    mobile_phone_number = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name='Мобільний номер',
    )

    class Meta:
        ordering = ['user']
        verbose_name = "Мобільний номер"
        verbose_name_plural = "Мобільні номери"

    def __str__(self):
        return self.user.username
