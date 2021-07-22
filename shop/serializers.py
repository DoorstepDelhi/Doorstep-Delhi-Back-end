from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from datetime import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Order, OrderLine, OrderEvent, Invoice, GiftCard, Voucher, Sale
from accounts.models import Address
from accounts.serializers import AddressSerializer, UserSerializer

class GiftCardSerializers(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault)
    created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = GiftCard
        fields = [
            'code',
            'user',
            'created',
            'start_date',
            'end_date',
            'last_used_on',
            'is_active',
            'initial_balance_amount',
            'current_balance_amount',
        ]
        

class OrderSerializer(serializers.ModelSerializer):
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault)
    created = serializers.DateTimeField(read_only=True)
    # gift_cards = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'created',
            'status',
            'user',
            'tracking_client_id',
            'billing_address',
            'shipping_address',
            'shipping_method',
            'shipping_price',
            'total_net_amount',
            'undiscounted_total_net_amount',
            'voucher',
            # 'gift_cards',
            'display_gross_prices',
            'customer_note',
        ]
        read_only_fields = ('id','tracking_client_id',)
        
    def invoices(self, obj):
        return

    def events(self, obj):
        return

    def products(self, obj):
        return


class OrderListSerializers(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = [
            'id',
            'created',
            'status',
            'tracking_client_id',
            'shipping_method',
            'total_net_amount',
        ]
        read_only_fields = ('id', 'tracking_client_id',)


class OrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = [
            'id',
            'order',
            'variant',
            'quantity',
            'quantity_fulfilled',
        ]


class OrderEventSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault)
    date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = OrderEvent
        fields = [
            'user',
            'date',
            'type',
            'order',
        ]


class InvoiceSerializers(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'order',
            'number',
            'created',
            'external_url',
            'invoice_file',
        ]


class GiftCardSerializers(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault)
    created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = GiftCard
        fields = [
            'code',
            'user',
            'created',
            'start_date',
            'end_date',
            'last_used_on',
            'is_active',
            'initial_balance_amount',
            'current_balance_amount',
        ]


class VoucherSerializers(serializers.ModelSerializer):

    class Meta:
        model = Voucher
        fields = [
            'type',
            'name',
            'code',
            'usage_limit',
            'used',
            'start_date',
            'end_date',
            'apply_once_per_order',
            'apply_once_per_customer',
            'discount_value_type',
            'min_checkout_items_quantity',
            'products',
            'collections',
            'categories',
        ]


class SaleSerializers(serializers.ModelSerializer):

    class Meta:
        model = Sale
        fields = [
            'name',
            'type',
            'products',
            'categories',
            'collections',
            'start_date',
            'end_date',
        ]


class CouponInputSerializers(serializers.Serializer):
    current_date = serializers.HiddenField(default=timezone.now)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault)
    code = serializers.CharField(max_length = 20)
    category = serializers.SerializerMethodField(read_only = True)

    def get_category(self):
        if self.code[:3]=="GFC":
            return "giftcard"
        else:
            return "voucher"

    def validate(self,data):
        if data['category']=="giftcard":
            code = get_object_or_404(GiftCard,code=data['code'])
            if not code:
                raise serializers.ValidationError("Invalid GiftCard")
            elif data['user'] != code.user :
                raise serializers.ValidationError("Giftcard doesn't link with current account")
            elif not (data['current_date'] >= code.start_date) :
                raise serializers.ValidationError("Using Giftcard early")
            elif not (data['current_date'] <= code.end_date) :
                raise serializers.ValidationError("Giftcard expired")
            else:
                return data

        else:
            code = get_object_or_404(Voucher,code=data['code'])
            if not code:
                raise serializers.ValidationError("Invalid Voucher")
            elif not (data['current_date'] >= code.start_date) :
                raise serializers.ValidationError("Using Voucher early")
            elif not (data['current_date'] <= code.end_date) :
                raise serializers.ValidationError("Voucher expired")
            elif not (code.used <= code.usage_limit):
                raise serializers.ValidationError("Voucher using limit surpassed")
            else:
                return data


class AddressInputSerializer(serializers.Serializer):
    default_address = serializers.SerializerMethodField(read_only = True)
    address = serializers.CharField(max_length=None, min_length=None, allow_blank=True, trim_whitespace=True)

    def get_default_address(self, obj):
        user = self.context['request'].user
        address = Address.objects.get(user=user)
        data = AddressSerializer(address).data
        return data

class PaymentSerializer(serializers.Serializer):
    date = serializers.HiddenField(default=timezone.now)


class OrderSummarySerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    wholesale_min_qty = serializers.SerializerMethodField()
    order_events = serializers.SerializerMethodField()


    class Meta:
        model = Order
        fields = [
            'product_name',
            'created',
            'price',
            'wholesale_min_qty',
            'id',
            'user_name',
            'total_net_amount',
            'status',
            'shipping_address',
            'order_events'
        ]

    def get_user_name(self,obj):
        return obj.user.first_name

    def get_product_name(self, obj):
        orderlines = OrderLine.objects.get(order = obj)
        product_name = orderlines.variant.product.name
        return product_name

    def get_shipping_address(self,obj):
        serializer = AddressSerializer(obj.user.default_shipping_address)
        return serializer.data
        

    def get_price(self, obj):
        orderlines = OrderLine.objects.get(order = obj)
        price = orderlines.variant.price
        return price


    def get_wholesale_min_qty(self, obj):
        orderlines = OrderLine.objects.get(order = obj)
        min_qty = orderlines. wholesale_variant.min_qty
        return min_qty
    

    def get_order_events(self, obj):
        orderevents = OrderEvent.objects.filter(order = obj)
        orderevents = orderevents.filter(
            type__in =map(lambda x:x.upper(), ['draft_created','placed','canceled','confirmed',
            'payment_refunded','payment_failed','reaching_pickup_point','reached_pickup_point'])
        )
        serializer = OrderEventSerializer(orderevents, many = True)
        return serializer.data