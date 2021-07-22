from decimal import Decimal
from datetime import date, datetime

from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save

from shop.choices import order_status_choices, order_event_type_choices, voucher_type_choices, discout_value_type_choices


class Order(models.Model):
    created = models.DateTimeField(default=now, editable=False)
    status = models.CharField(
        max_length=32, default="unfulfilled", choices=order_status_choices)
    user = models.ForeignKey(
        "accounts.User",
        blank=True,
        null=True,
        related_name="orders",
        on_delete=models.SET_NULL,
    )
    tracking_client_id = models.CharField(max_length=36, blank=True, editable=False)
    billing_address = models.ForeignKey(
        "accounts.Address", related_name="+", editable=False, null=True, on_delete=models.SET_NULL
    )
    shipping_address = models.ForeignKey(
        "accounts.Address", related_name="+", editable=False, null=True, on_delete=models.SET_NULL
    )
    pickup_point = models.ForeignKey(
        'store.PickupPoint', related_name="orders", null=True, on_delete=models.SET_NULL
    )
    shipping_method = models.ForeignKey(
        "store.ShippingMethod",
        blank=True,
        null=True,
        related_name="orders",
        on_delete=models.SET_NULL,
    )
    shipping_price = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
        editable=False,
    )
    total_net_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    undiscounted_total_net_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    voucher = models.ForeignKey(
        "shop.Voucher", blank=True, null=True, related_name="+", on_delete=models.SET_NULL
    )
    gift_cards = models.ManyToManyField("shop.GiftCard", blank=True, related_name="orders")
    display_gross_prices = models.BooleanField(default=True)
    customer_note = models.TextField(blank=True, default="")


def save_order(sender, instance, **kwargs):
    clientID = instance.created.strftime("DRSDL%Y%m%d%H") + str(instance.id)
    instance.tracking_client_id = clientID


post_save.connect(save_order, sender=Order)


class OrderLine(models.Model):
    order = models.ForeignKey(
        Order, related_name="lines", editable=False, on_delete=models.CASCADE, null=True
    )
    variant = models.ForeignKey(
        "product.ProductVariant",
        related_name="order_lines",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    quantity_fulfilled = models.IntegerField(
        validators=[MinValueValidator(0)], default=0
    )

    def increment_quantity_by_one(self,order:order,variant:variant):
        orderline, _is_created = self.items.get(id=id, order=order)
        current_quantity = orderline.quantity
        orderline.update(quantity=current_quantity+1)
        orderline.save()
        return orderline


class OrderEvent(models.Model):
    """Model used to store events that happened during the order lifecycle.

    Args:
        parameters: Values needed to display the event on the storefront
        type: Type of an order

    """

    date = models.DateTimeField(default=now, editable=False)
    type = models.CharField(
        max_length=255,
        choices=[
            (type_name.upper(), type_name) for type_name, _ in order_event_type_choices
        ],
    )
    order = models.ForeignKey(Order, related_name="events", on_delete=models.CASCADE)
    user = models.ForeignKey(
        "accounts.User",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    def __str__(self) -> str:
        return self.type


class Invoice(models.Model):
    order = models.ForeignKey(
        Order, related_name="invoices", null=True, on_delete=models.SET_NULL
    )
    number = models.CharField(max_length=255, null=True)
    created = models.DateTimeField(null=True)
    external_url = models.URLField(null=True, max_length=2048)
    invoice_file = models.FileField(upload_to="invoices")


class GiftCard(models.Model):
    code = models.CharField(max_length=16, unique=True, db_index=True)
    user = models.ForeignKey(
        "accounts.User",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="gift_cards",
    )
    created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(null=True, blank=True)
    last_used_on = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    initial_balance_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
    )

    current_balance_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
    )


class Voucher(models.Model):
    type = models.CharField(
        max_length=20, choices=voucher_type_choices, default="entire_order"
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    value = models.PositiveSmallIntegerField(null=True)
    code = models.CharField(max_length=12, unique=True, db_index=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used = models.PositiveIntegerField(default=0, editable=False)
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField(null=True, blank=True)
    # this field indicates if discount should be applied per order or
    # individually to every item
    apply_once_per_order = models.BooleanField(default=False)
    apply_once_per_customer = models.BooleanField(default=False)

    discount_value_type = models.CharField(
        max_length=10,
        choices=discout_value_type_choices,
        default="fixed",
    )

    # not mandatory fields, usage depends on type
    min_checkout_items_quantity = models.PositiveIntegerField(null=True, blank=True)
    products = models.ManyToManyField("product.Product", blank=True)
    collections = models.ManyToManyField("product.Collection", blank=True)
    categories = models.ManyToManyField("product.Category", blank=True)


class Sale(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=10,
        choices=discout_value_type_choices,
        default="fixed",
    )
    products = models.ManyToManyField("product.Product", blank=True)
    categories = models.ManyToManyField("product.Category", blank=True)
    collections = models.ManyToManyField("product.Collection", blank=True)
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField(null=True, blank=True)