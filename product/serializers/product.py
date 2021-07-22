from django.db.models import Q
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from product.models import (
    Category,
    SubCategory,
    ProductType,
    Variation,
    Customization,
    Product,
    ProductVariant,
    ProductImage,
    VariantImage,
    CollectionProduct,
    Collection,
    ProductReview,
    ProductReviewFile,
    Brand
)
# from product.serializers.category import VariationSerializer


class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = ["id","name"]


class ProductListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    min_qty = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "average_rating",
            "image",
            "min_qty",
            "min_price",
        ]

    def get_min_price(self, obj):
        return obj.min_price

    def get_min_qty(self, obj):
        return obj.lowest_min_qty

    def get_image(self, obj):
        image = ProductImage.objects.filter(product=obj)
        if image.exists():
            image = image[0]
            data = {
                'url': image.image.url,
                'alt': image.alt,
            }
            return data
        return None
