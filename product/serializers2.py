from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from product.models import (
    Category,
    SubCategory,
    ProductType,
    Variation,
    Customization,
    Product,
    ProductPrice,
    ProductVariant,
    ProductImage,
    VariantImage,
    CollectionProduct,
    Collection,
    ProductReview,
    ProductReviewFile,
    Brand
)
from store.serializers import StoreSerializer

from product.serializers.category import CategoryListSerializer
from product.serializers.product import ProductListSerializer


class ProductTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductType
        fields = [
            "id",
            "name",
            "has_variants",
            "is_shipping_required",
            "is_digital",
            "is_wholesale_product",
            "qty_type",
            "tax_percentage",
            "products"
        ]


class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = ["id", "name"]


class CustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customization
        fields = ["id", "name", "description"]


class ProductSerializer(serializers.ModelSerializer):
    product_type = ProductTypeSerializer()
    category = CategoryListSerializer()
    variations = VariationSerializer()
    customization = CustomizationSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "product_type",
            "name",
            "description",
            "category",
            "updated_at",
            "charge_taxes",
            "product_qty",
            "default_variant",
            "visible_in_listings",
            "variations",
            "customization",
        ]

    def create(self, validated_data):
        product_type = validated_data.pop("product_type")
        category = validated_data.pop("category")
        variations = validated_data.pop("variations")
        customization = validated_data.pop("customization")
        products = Product.objects.create(**validated_data)
        for product in products:
            Product.objects.create(
                product_type=product_type,
                category=category,
                variations=variations,
                customizations=customization,
                **product
            )
        return products


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "alt",
        ]


class ProductVariantSerializer(serializers.ModelSerializer):
    variant = VariationSerializer()
    images = ProductImageSerializer(many=True)

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "name",
            "product",
            "variant",
            "images",
            "track_inventory",
            "product_qty",
            "price",
            "discounted_price",
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductReview
        fields = [
            "user",
            "product",
            "rating",
            "review",
            'files',
        ]

    def get_files(self, obj):
        files = ProductReviewFile.objects.filter(review=obj).values_list('file', flat=True)
        print(files)
        return files


class ReviewInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = [
            "rating",
            "review",
        ]


class BrandListSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField(read_only=True)
    products = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ["id", "color", "name", "image", "alt", "average_rating", "products_count", "products"]

    def get_products_count(self, obj):
        count = products = Product.objects.filter(brand=obj).count()
        return count

    def get_products(self, obj):
        products = Product.objects.filter(brand=obj)[:10]
        serializer = ProductListSerializer(products, many=True, context=self.context)
        return serializer.data


class BrandDetailSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ["id", "color", "name", "image", "alt", "description", "products", "reviews"]

    def get_products(self, obj):
        products = Product.objects.filter(brand=obj)
        serializer = ProductListSerializer(products, many=True)
        return serializer.data

    def get_reviews(self, obj):
        reviews = ProductReview.objects.filter(product__brand=obj)
        serializer = ProductReviewSerializer(reviews, many=True)
        return serializer.data


class ProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = (
            "product",
            "min_qty",
            "price",
            "discounted_price"
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    product_type = ProductTypeSerializer()
    category = CategoryListSerializer()
    variations = VariationSerializer()
    customization = CustomizationSerializer(read_only=True, many=True)
    variants = serializers.SerializerMethodField(read_only=True)
    reviews = serializers.SerializerMethodField(read_only=True)
    brand = BrandListSerializer()
    prices = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'product_type',
            'category',
            'variations',
            'brand',
            'customization',
            'name',
            'description',
            'updated_at',
            'charge_taxes',
            'product_qty',
            'visible_in_listings',
            'variants',
            'reviews',
            'prices',

        ]

    def create(self, validated_data):
        product_type = validated_data.pop("product_type")
        category = validated_data.pop("category")
        variations = validated_data.pop("variations")
        customization = validated_data.pop("customization")
        products = Product.objects.create(**validated_data)
        for product in products:
            Product.objects.create(
                product_type=product_type,
                category=category,
                variations=variations,
                customizations=customization,
                **product
            )
        return products

    def get_prices(self, obj):
        prices = ProductPrice.objects.filter(product=obj)
        serializer = ProductPriceSerializer(prices, many=True)
        return serializer.data

    def get_variants(self, obj):
        variants = ProductVariant.objects.filter(product=obj)
        serializer = ProductVariantSerializer(variants, many=True)
        return serializer.data

    def get_reviews(self, obj):
        reviews = ProductReview.objects.filter(product=obj)
        serializer = ProductReviewSerializer(reviews, many=True)
        return serializer.data


class CollectionSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True)

    class Meta:
        model = Collection
        fields = [
            "id",
            "name",
            "products",
            "background_image",
            "background_image_alt",
            "description",
        ]