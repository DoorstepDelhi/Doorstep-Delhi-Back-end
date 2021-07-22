from django.db.models import Q
from rest_framework import serializers
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
from product.serializers.product import ProductListSerializer


class CategoryListSerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField(read_only=True)
    products = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "icon",
            "sub_categories",
            "products",
        ]

    def get_sub_categories(self, obj):
        sub_categories = SubCategory.objects.filter(category=obj)
        serializer = SubCategoryListSerializer(sub_categories, many=True)
        return serializer.data

    def get_products(self, obj):
        products = Product.objects.filter(Q(category=obj) | Q(sub_category__category=obj))[:10]
        serializer = ProductListSerializer(products, many=True)
        return serializer.data


class CategoryDetailSerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "icon",
            "sub_categories",
        ]

    def get_sub_categories(self, obj):
        sub_categories = SubCategory.objects.filter(category=obj)
        serializer = SubCategoryDetailSerializer(sub_categories, many=True)
        return serializer.data


class SubCategoryListSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubCategory
        fields = [
            "id",
            "name",
        ]


class SubCategoryDetailSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SubCategory
        fields = [
            "id",
            "name",
            "products",
        ]

    def get_products(self, obj):
        products = Product.objects.filter(sub_category=obj)
        serializer = ProductListSerializer(products, many=True)
        return serializer.data


class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = ["id","name"]