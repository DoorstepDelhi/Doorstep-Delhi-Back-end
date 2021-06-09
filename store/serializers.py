from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from datetime import datetime
from .models import Store, ShippingZone, ShippingMethod
from accounts.models import Address
from accounts.serializers import AddressSerializer,AddressSerializer
from accounts.models import Address, User


class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = [
            'name',
            'type',
            'shipping_zone',
            'excluded_products',
            'maximum_delivery_days',
            'minimum_delivery_days',
        ]


class ShippingZoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShippingZone
        fields = [
            'name',
            'countries',
            'default',
            'description',
        ]


class StoreSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Store 
        fields = [
            'name',
            'email',
            'users',
            'address',
            'created_at',
            'shipping_zones'
        ]

class FullRegisterStoreSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Store 
        fields = [
            'name',
            'email',
            'users',
            'created_at',
            'shipping_zones'
        ]

class PickupPointListSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Store
        fields = [
            'name',
            'email',
            'user',
            'address',
            'opening_time',
            'closing_time',
            'created_at',
        ]


class PickupPointSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Store
        fields = [
            'name',
            'email',
            'user',
            'user_aadhaar',
            'address',
            'opening_time',
            'closing_time',
            'created_at',
        ]