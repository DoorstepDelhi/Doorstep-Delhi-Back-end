from django.db import models
from django_measurement.models import MeasurementField
from versatileimagefield.fields import VersatileImageField
from django.db.models import Avg, Min
from django.utils.functional import cached_property


class Category(models.Model):
    name = models.CharField(max_length=250)
    icon = models.CharField(max_length=15)
    verified = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class SubCategory(models.Model):
    category = models.ForeignKey("product.Category", on_delete=models.PROTECT)
    name = models.CharField(max_length=250)
    verified = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Sub-Categories"


class Brand(models.Model):
    name = models.CharField(max_length=250, unique=True)
    image = models.ImageField(upload_to="brands", blank=False)
    alt = models.CharField(max_length=128, blank=True)
    description = models.TextField()
    color = models.CharField(max_length=32)

    def average_rating(self):  # returns avg rating of all products of a brand
        ratings = ProductReview.objects.filter(product__brand__id=self.id).aggregate(ratings=Avg('rating'))
        rating = ratings['ratings']
        return rating

    def __str__(self) -> str:
        return self.name


class ProductType(models.Model):
    name = models.CharField(max_length=250)
    has_variants = models.BooleanField(default=True)
    is_shipping_required = models.BooleanField(default=True)
    is_digital = models.BooleanField(default=False)
    is_wholesale_product = models.BooleanField(default=False)
    qty_type = models.CharField(max_length=256)
    tax_percentage = models.FloatField()

    def __str__(self) -> str:
        return self.name


class Variation(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Customization(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name


class Product(models.Model):
    product_type = models.ForeignKey(
        ProductType, related_name="products", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    sub_category = models.ForeignKey(
        "product.SubCategory",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True, null=True)
    charge_taxes = models.BooleanField(default=True)
    product_qty = models.FloatField()
    default_variant = models.OneToOneField(
        "ProductVariant",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    visible_in_listings = models.BooleanField(default=False)
    variations = models.ManyToManyField("product.Variation")
    customizations = models.ManyToManyField("product.Customization")
    views = models.IntegerField(default=0)

    def __iter__(self):
        if not hasattr(self, "__variants"):
            setattr(self, "__variants", self.variants.all())
        return iter(getattr(self, "__variants"))

    def __str__(self) -> str:
        return self.name

    def average_rating(self):
        avg_rating = ProductReview.objects.filter(product__id=self.id).aggregate(ratings=Avg('rating'))
        rating = avg_rating.get("ratings")
        return rating

    @staticmethod
    def cheapest_product_variant(self):
        cheapest_variant = ProductVariant.objects.filter(product__id=self.id).aggregate(Min('discounted_price'))
        return cheapest_variant

    @cached_property
    def lowest_min_qty(self):
        min_qty = ProductPrice.objects.filter(product=self).aggregate(Min('min_qty'))['min_qty__min']
        return min_qty

    @cached_property
    def min_price(self):
        min_price = ProductPrice.objects.filter(product=self).aggregate(Min('discounted_price'))[
            'discounted_price__min']
        return min_price


class ProductPrice(models.Model):
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE)
    min_qty = models.PositiveSmallIntegerField(default=1)
    price = models.PositiveBigIntegerField()
    discounted_price = models.PositiveBigIntegerField()
    store = models.ForeignKey(
        "store.Store", related_name="wholesale_products", on_delete=models.CASCADE, null=True
    )

# class VariantChoice(models.Model):
#     name = models.CharField(max_length=255, blank=True)
#     variation = models.ForeignKey(
#             "product.Variation", related_name="products", on_delete=models.PROTECT
#     )


class ProductVariant(models.Model):
    name = models.CharField(max_length=255, blank=True)
    product = models.ForeignKey(
        "product.Product", related_name="variants", on_delete=models.CASCADE
    )
    variant = models.ForeignKey(
        "product.Variation", related_name="products", on_delete=models.PROTECT
    )
    images = models.ManyToManyField("ProductImage", through="VariantImage")
    track_inventory = models.BooleanField(default=True)
    product_qty = models.FloatField()
    price = models.FloatField()
    discounted_price = models.FloatField()

    def __str__(self):
        return str(self.product) + "-" + self.name

    def get_images(self):
        return "\n".join([p.__str__() for p in self.images.all()])


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products", blank=False)
    # image = VersatileImageField(upload_to="products", ppoi_field="ppoi", blank=False)
    alt = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return str(self.product) + "-" + self.alt


class VariantImage(models.Model):
    variant = models.ForeignKey(
        "ProductVariant", related_name="variant_images", on_delete=models.CASCADE
    )
    image = models.ForeignKey(
        ProductImage, related_name="variant_images", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("variant", "image")


class ProductReview(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class ProductReviewFile(models.Model):
    review = models.ForeignKey("product.ProductReview", on_delete=models.CASCADE)
    file = models.FileField(upload_to="reviews")


class CollectionProduct(models.Model):
    collection = models.ForeignKey(
        "Collection", related_name="collectionproduct", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="collectionproduct", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (("collection", "product"),)


class Collection(models.Model):
    name = models.CharField(max_length=250, unique=True)
    products = models.ManyToManyField(
        "product.Product",
        blank=True,
        related_name="collections",
        through=CollectionProduct,
        through_fields=("collection", "product"),
    )
    background_image = models.ImageField(upload_to="collection-backgrounds", blank=True, null=True)
    # background_image = VersatileImageField(
    #     upload_to="collection-backgrounds", blank=True, null=True
    # )
    background_image_alt = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True, null=True)
