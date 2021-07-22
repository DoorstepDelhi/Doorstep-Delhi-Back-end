from django.db import models

from product.models import Product, ProductVariant


class Wishlist(models.Model):
    user = models.OneToOneField(
        "accounts.User",
        related_name="wishlist",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def set_user(self, user):
        self.user = user
        self.save()

    def get_all_variants(self):
        return ProductVariant.objects.filter(
            wishlist_items__wishlist_id=self.pk
        ).distinct()

    def add_product(self, product: Product):
        item, _is_created = self.items.get_or_create(product_id=product.pk)
        return item

    def remove_product(self, product: Product):
        self.items.filter(product_id=product.pk).delete()

    def add_variant(self, variant: ProductVariant):
        item, _is_created = self.items.get_or_create(product_id=variant.product_id)
        item.variants.add(variant)
        return item

    def remove_variant(self, variant: ProductVariant):
        try:
            item = self.items.get(product_id=variant.product_id)
        except WishlistItem.DoesNotExist:
            return
        else:
            item.variants.remove(variant)
            # If it was the last variant, delete the whole item
            if item.variants.count() == 0:
                item.delete()


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist, related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "product.Product", related_name="wishlist_items", on_delete=models.CASCADE
    )
    variants = models.ManyToManyField(
        "product.ProductVariant", related_name="wishlist_items", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("wishlist", "product")

    def __str__(self):
        return "WishlistItem (%s, %s)" % (self.wishlist.user, self.product)
