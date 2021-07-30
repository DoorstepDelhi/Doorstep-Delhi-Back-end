from django.db import models
from shop.serializers import OrderSerializer
from typing import AsyncContextManager
from rest_framework import serializers
from room.models import Message, Room, RoomRecommendedProduct, RoomUser,RoomWishlistProduct,WishlistProductVote,RoomOrder, RoomOrderLine, UserOrderLine, OrderEvent,Invoice, Message
from product.serializers2 import ProductListSerializer
from accounts.serializers import AddressSerializer, UserSerializer, UserListSerializer
from store.serializers import PickupPointSerializer, ShippingMethodSerializer


class RoomSerializer(serializers.ModelSerializer):
    created_at = serializers.ReadOnlyField()

    class Meta:
        model = Room
        fields = [
            "id",
            "name",
            "title",
            "description",
            "image",
            "created_at",
            "deleted_at",
        ]


class RoomRecommendationsSerializer(serializers.ModelSerializer):
    product = ProductListSerializer()

    class Meta:
        model = RoomRecommendedProduct
        fields = [
            "id",
            "product",
            "variants",
            "priority",
        ]


class RoomListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = [
            "id",
            "name",
            "title",
            "image",
        ]


class RoomLastMessageSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(read_only=True)
    unseen_messages = serializers.SerializerMethodField(read_only=True)
    is_admin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Room
        fields = [
            "id",
            "name",
            "title",
            "image",
            "last_message",
            "unseen_messages",
            "is_admin",
        ]

    def get_last_message(self, obj):
        message = Message.objects.filter(room=obj).first()
        serializer = MessageSerializer([message], many=True)
        return serializer.data

    def get_unseen_messages(self, obj):
        request = self.context.get('request', None)
        user = request.user
        if user:
            room_user = RoomUser.objects.get(user=user, room=obj)
            messages = Message.objects.filter(room=obj, created_on__gte=room_user.viewed_at)
            if messages.exists():
                return messages.count()
        return None

    def get_is_admin(self, obj):
        request = self.context.get("request", None)
        user = request.user
        return True


class RoomUserSerializer(serializers.ModelSerializer):
    # user = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )
    user = UserSerializer()
    joined_at = serializers.ReadOnlyField()

    class Meta:
        model = RoomUser
        fields = [
            "id",
            "user",
            "role",
            "joined_at",
            "left_at"
        ]


class RoomWishlistProductSerializer(serializers.ModelSerializer):
    product = ProductListSerializer()
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = RoomWishlistProduct
        fields = [
            "id",
            "room",
            "product",
            "user",
            "votes",
        ]


class WishlistProductVoteSerializer(serializers.ModelSerializer):
    product = RoomWishlistProductSerializer()
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = WishlistProductVote
        fields = [
            "id",
            "product",
            "user"
        ]


class RoomOrderSerializer(serializers.ModelSerializer):
    room = RoomSerializer()
    billing_address = AddressSerializer()
    shipping_address = AddressSerializer()
    pickup_point = PickupPointSerializer()
    shipping_method = ShippingMethodSerializer()

    class Meta:
        model = RoomOrder
        fields = [
            "id",
            "room",
            "status",
            "tracking_client_id",
            "billing_address",
            "shipping_address",
            "pickup_point",
            "shipping_method",
            "shipping_price",
            "total_net_amount",
            "undiscounted_total_net_amount"
        ]


class RoomOrderLineSerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    created_at = serializers.ReadOnlyField()

    class Meta:
        model = RoomOrderLine
        fields = [
            "id",
            "order",
            "variant",
            "created_at"
        ]


class UserOrderLineSerializer(serializers.ModelSerializer):
    product = RoomOrderLineSerializer()
    updated_at = serializers.ReadOnlyField()

    class Meta:
        model = UserOrderLine
        fields = [
            "id",
            "product",
            "quantity",
            "quantity_fulfilled",
            "updated_at",
        ]


class OrderEventSerializer(serializers.ModelSerializer):
    order = RoomOrderSerializer()
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = OrderEvent
        fields = [
            "id",
            "date",
            "type",
            "order",
            "user",
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    order = RoomOrderSerializer()
    invoice_file = serializers.FileField()
    externl_url = serializers.URLField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "order",
            "number",
            "created",
            "external_url",
            "invoice_file"
        ]


class MessageSerializer(serializers.ModelSerializer):
    file_field = serializers.FileField(allow_empty_file = True)
    created_on = serializers.SerializerMethodField(read_only=True)
    user = UserListSerializer()
    type = serializers.SerializerMethodField(read_only=True)
    product = ProductListSerializer()

    class Meta:
        model = Message
        fields = [
            "id",
            "type",
            "file_field",
            "message_text",
            "product",
            "user",
            "created_on",
            "room"
        ]

    @staticmethod
    def get_type(self):
        return "send_to_websocket"

    def get_created_on(self, obj):
        return obj.created_on.strftime("%d %b %Y %H:%M:%S %Z")
