from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict

from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField
from versatileimagefield.fields import VersatileImageField


class User(AbstractUser):
    profile_pic = VersatileImageField(
        upload_to="users", blank=True, null=True
    )
    default_shipping_address = models.ForeignKey(
        "accounts.Address",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    default_billing_address = models.ForeignKey(
        "accounts.Address",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def city(self):
        if self.default_billing_address:
            return str(self.default_billing_address.city)
        return ""


notification_lang_choices = (
    ("hi", "hi"),
    ("en", "en"),
    ("na", "na")
)
class UserPreference(models.Model):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE)
    notification_lang = models.CharField(max_length=2, choices=notification_lang_choices, default="en")


class Address(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=512, blank=True)
    street_address_1 = models.CharField(max_length=256, blank=True)
    street_address_2 = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=256, blank=True)
    state = models.CharField(max_length=128, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    class Meta:
        ordering = ("pk",)

    def __str__(self):
        return self.full_name
