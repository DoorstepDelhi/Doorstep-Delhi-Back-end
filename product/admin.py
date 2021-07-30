from django.contrib import admin
import nested_admin

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
    ProductReview,
    ProductReviewFile,
    CollectionProduct,
    Collection,
)

from product.forms import ProductImageForm


class CollectionAdmin(nested_admin.NestedModelAdmin):
    list_display = [
                    'name',
                    ]
    list_display_links = [
                    'name',
                    ]
    search_fields = [
                    'name',
                    'description',
                    ]


class ProductReviewFileInline(nested_admin.NestedTabularInline):
    model = ProductReviewFile
    extra = 0


class ProductReviewInline(nested_admin.NestedTabularInline):
    model = ProductReview
    inlines = [ProductReviewFileInline]
    extra = 0


class ProductImageInline(nested_admin.NestedTabularInline):
    # form = ProductImageForm
    model = ProductImage
    extra = 0


class VariantImageInline(nested_admin.NestedTabularInline):
    model = VariantImage
    extra = 0

class ProductVariantInline(nested_admin.NestedTabularInline):
    model = ProductVariant
    list_display = ['__all__']
    inlines = [VariantImageInline]
    extra = 0

class ProductVariantAdmin(nested_admin.NestedModelAdmin):
    list_display = ['id', 'name','product', 'variant','track_inventory', 'product_qty', 'price', 'discounted_price',"get_images"]

class ProductInline(nested_admin.NestedTabularInline):
    model = Product
    inlines = [
        ProductVariantInline,
        ProductImageInline,
        ProductReviewInline,
    ]
    extra = 0


class ProductAdmin(nested_admin.NestedModelAdmin):
    inlines = [
        ProductVariantInline,
        ProductImageInline,
        ProductReviewInline,
    ]
    list_display = [
        'id',
        'category',
        'name',
    ]
    list_display_links = [
        'category',
        'name',
    ]
    search_fields = [
        'name',
    ]
    list_filter = [
                    'category',
                    ]


class SubCategoryInline(nested_admin.NestedTabularInline):
    model = SubCategory
    inlines = [
        ProductInline
    ]
    extra = 0


class SubCategoryAdmin(nested_admin.NestedModelAdmin):
    inlines = [ProductInline]
    list_display = [
                    'id',
                    'name',
                    ]
    list_display_links = [
                    'name',
                    ]
    search_fields = [
                    'name',
                    ]


class CategoryAdmin(nested_admin.NestedModelAdmin):
    inlines = [SubCategoryInline, ProductInline]
    list_display = [
                    'id',
                    'name',
                    ]
    list_display_links = [
                    'name',
                    ]
    search_fields = [
                    'name',
                    ]


class ProductTypeAdmin(nested_admin.NestedModelAdmin):
    inlines = [ProductInline]
    list_display = [
                    'name',
                    'has_variants',
                    'is_shipping_required',
                    'is_wholesale_product',
                    'qty_type',
                    'tax_percentage',
                    ]
    list_editable = [
                    'is_wholesale_product',
                    'qty_type',
                    'tax_percentage',
                    ]
    list_display_links = [
                    'name',
                    ]
    list_filter = [
                    'has_variants',
                    'is_shipping_required',
                    'is_digital',
                    'is_wholesale_product',
                    'qty_type',
                    'tax_percentage',
                    ]
    search_fields = [
                    'name',
                    'qty_type',
                    ]


class VariationAdmin(nested_admin.NestedModelAdmin):
    list_display = [
                    'name',
                    ]
    list_display_links = [
                    'name',
                    ]
    search_fields = [
                    'name',
                    ]


class CustomizationAdmin(nested_admin.NestedModelAdmin):
    list_display = [
                    'name',
                    ]
    list_display_links = [
                    'name',
                    ]
    search_fields = [
                    'name',
                    'description',
                    ]


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Customization, CustomizationAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
