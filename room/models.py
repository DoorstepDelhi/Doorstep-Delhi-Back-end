from datetime import datetime
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils.timezone import now
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save

from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from shop.choices import order_status_choices, order_event_type_choices, voucher_type_choices, \
    discout_value_type_choices
from product.serializers.product import ProductListSerializer


class Room(models.Model):
    name = models.CharField(max_length=150)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    users = models.ManyToManyField("accounts.User", through="room.RoomUser")
    private = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class RoomRecommendedProduct(models.Model):
    room = models.ForeignKey("room.Room", on_delete=models.CASCADE)
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE)
    variants = models.ManyToManyField("product.ProductVariant")
    priority = models.PositiveSmallIntegerField(default=1)


user_role_choices = (
    ("A", "Admin"),
    ("U", "User"),
)


class RoomUser(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    room = models.ForeignKey("room.Room", on_delete=models.CASCADE, related_name='room_users')
    role = models.CharField(max_length=2, choices=user_role_choices)
    viewed_at = models.DateTimeField(auto_now=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'room')

    def __str__(self):
        return self.room.name


class RoomWishlistProduct(models.Model):
    room = models.ForeignKey('room.Room', on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', null=True, blank=True, on_delete=models.SET_NULL)
    added_at = models.DateTimeField(auto_now_add=True)
    votes = models.PositiveSmallIntegerField(default=0)
    voted_by = models.ManyToManyField("accounts.User", through="room.WishlistProductVote", related_name="voted_products")

    def __str__(self):
        return self.product.name

    class Meta:
        unique_together = ("room", "product")


class WishlistProductVote(models.Model):
    product = models.ForeignKey('room.RoomWishlistProduct', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.product.product.name

    class Meta:
        unique_together = ("product", "user")


class RoomOrder(models.Model):
    room = models.ForeignKey("room.Room", on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(default=now, editable=False)
    status = models.CharField(
        max_length=32, default="unfulfilled", choices=order_status_choices)
    tracking_client_id = models.CharField(max_length=36, blank=True, editable=False)
    billing_address = models.ForeignKey(
        "accounts.Address", related_name="+", editable=False, null=True, on_delete=models.SET_NULL
    )
    shipping_address = models.ForeignKey(
        "accounts.Address", related_name="+", editable=False, null=True, on_delete=models.SET_NULL
    )
    pickup_point = models.ForeignKey(
        'store.PickupPoint', related_name="pickup_point", null=True, on_delete=models.SET_NULL
    )
    shipping_method = models.ForeignKey(
        "store.ShippingMethod",
        blank=True,
        null=True,
        related_name="shipping_method",
        on_delete=models.SET_NULL,
    )
    shipping_price = models.PositiveSmallIntegerField(
        default=0,
    )
    total_net_amount = models.PositiveBigIntegerField(
        default=0,
    )
    undiscounted_total_net_amount = models.PositiveBigIntegerField(
        default=0,
    )


class RoomOrderLine(models.Model):
    order = models.ForeignKey(
        'room.RoomOrder', related_name="lines", editable=False, on_delete=models.CASCADE, null=True
    )
    user = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(
        "product.Product",
        related_name="order_line_products",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=32, default="unfulfilled", choices=order_status_choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('order', "product")

    @property
    def group_quantity(self):
        quantity = RoomOrderLineVariant.objects.filter(order_line=self).aggregate(quantity=Sum('group_quantity'))['quantity']
        return quantity

    def user_quantity(self, user):
        variants = RoomOrderLineVariant.objects.filter(order_line=self)
        quantity = 0
        for variant in variants:
            quantity += variant.user_quantity(user)
        return quantity


class RoomOrderLineVariant(models.Model):
    order_line = models.ForeignKey(
        'room.RoomOrderLine', related_name="line_variants", editable=False, on_delete=models.CASCADE, null=True
    )
    variants = models.ManyToManyField(
        "product.ProductVariant",
    )

    @property
    def group_quantity(self):
        quantity = UserOrderLine.objects.filter(product=self).aggregate(quantity=Sum('quantity'))['quantity']
        return quantity

    def user_quantity(self, user):
        user_order_line = UserOrderLine.objects.get(user=user, product=self)
        return user_order_line.quantity


class UserOrderLine(models.Model):
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey('room.RoomOrderLineVariant', related_name='users_quantity', on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    quantity_fulfilled = models.IntegerField(
        validators=[MinValueValidator(0)], default=0
    )
    updated_at = models.DateTimeField(auto_now=True)
    customization = models.TextField(null=True, blank=True)
    file = models.FileField(null=True, blank=True, upload_to="group_orders")

    class Meta:
        unique_together = ('user', 'product')


class OrderEvent(models.Model):
    date = models.DateTimeField(default=now, editable=False)
    type = models.CharField(
        max_length=255,
        choices=[
            (type_name.upper(), type_name) for type_name, _ in order_event_type_choices
        ],
    )
    order = models.ForeignKey("room.RoomOrder", related_name="events", on_delete=models.CASCADE)
    user = models.ForeignKey(
        "accounts.User",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )


class Invoice(models.Model):
    order = models.ForeignKey(
        "room.RoomOrder", related_name="invoices", null=True, on_delete=models.SET_NULL
    )
    number = models.CharField(max_length=255, null=True)
    created = models.DateTimeField(null=True)
    external_url = models.URLField(null=True, max_length=2048)
    invoice_file = models.FileField(upload_to="invoices")


class Message(models.Model):
    room = models.ForeignKey('room.Room', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product', on_delete= models.CASCADE, null = True)
    file_field = models.FileField(upload_to='messages', blank=True, null=True)
    message_text = models.CharField(max_length=1000, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.__str__() + " : " + self.message_text


# @receiver(post_save, sender=Message, dispatch_uid="send_recommendsations")
# def send_notification(sender, instance, **kwargs):
#     if instance.message_text:
#         print("Starting reading message")
#         room_group_name = 'recommendations_%s' % instance.room.name
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             room_group_name, {
#                 'type': "send_room_recommendations",
#                 'message': instance.message_text
#             }
#         )

class ReportGroup(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    room = models.ForeignKey('room.Room', on_delete = models.CASCADE)
    date_time = models.DateTimeField(auto_now=True)