from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from datetime import datetime
from .models import BankAccount, Store, ShippingZone, ShippingMethod
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
            # 'id',
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
            'shipping_zones',
            'logo',
            'website',
            'facebook_link',
            'instagram_link'
        ]
        
class BusinessSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Store 
        fields = [
            'name',
            'email',
            'created_at',
            'logo',
            'website',
            'facebook_link',
            'instagram_link'
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
        
                
        
class BankAccountSerializer(serializers.ModelSerializer):
    # store = StoreSerializer(read_only =True)
    store = serializers.HiddenField(default=serializers.CurrentUserDefault)
    
    class Meta:
        model = BankAccount
        fields = [
            'store',
            'holder_name',
            'account_number',
            'ifsc',
            'account_type',
            'bank_name'
        ]
        
# class ProfileSerializer(serializers.ModelSerializer):
#     store_name = serializers.SerializerMethodField('get_store_name')
#     address = AddressSerializer()
#     bank_details = BankAccountSeriaalizer()
#     shipping_method = ShippingMethodSerializer()
#     shipping_zone = ShippingZoneSerializer()
#     class Meta:
#         model = Store
#         fields =[
#             'store_name',
#             'email',
#             'address',
#             'bank_details',
#             'shipping_method',
#             'shipping_zone',
#         ]
    
#     def get_store_name(self,obj):
#         return obj.name