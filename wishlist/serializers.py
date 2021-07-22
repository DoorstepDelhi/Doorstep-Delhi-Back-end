from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from datetime import datetime

from wishlist.models import Wishlist, WishlistItem
from product.serializers.product import ProductListSerializer


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer()

    class Meta:
        model = WishlistItem
        fields = (
            "id",
            "product",
            "created_at",
        )
