from faker import Faker

from accounts.models import User
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
    ProductReview,
    ProductReviewFile,
    CollectionProduct,
    Collection,
    Brand,
)
from store.models import Store
from .categories import add_categories

fake = Faker()
Faker.seed(999)


def populate(n):
    add_categories()
    add_sub_categories(50)
    add_product_types()
    add_variations()
    add_customizations()
    add_brands()
    add_products(n)
    # add_review_file(n)
    add_collections()
    add_collection_products(n)


def add_sub_categories(N):
    categories = Category.objects.all()
    categories_count = categories.count()
    SubCategory.objects.bulk_create(
        [
            SubCategory(
                name=fake.word(),
                category=categories[fake.random_int(max=categories_count - 1)]
            )
            for _ in range(N)
        ]
    )


def add_product_types():
    ProductType.objects.bulk_create(
        [
            ProductType(
                name="Book",
                has_variants=True,
                is_shipping_required=True,
                is_digital=False,
                is_wholesale_product=True,
                qty_type="Pieces",
                tax_percentage=12.0
            ),
            ProductType(
                name="E-Book",
                has_variants=True,
                is_shipping_required=False,
                is_digital=True,
                is_wholesale_product=False,
                qty_type="Pieces",
                tax_percentage=12.0
            ),
            ProductType(
                name="Clothing",
                has_variants=True,
                is_shipping_required=True,
                is_digital=False,
                is_wholesale_product=True,
                qty_type="Pieces",
                tax_percentage=18.0
            ),
            ProductType(
                name="Office Supplies",
                has_variants=True,
                is_shipping_required=True,
                is_digital=False,
                is_wholesale_product=True,
                qty_type="Pieces",
                tax_percentage=5.0
            ),
        ]
    )


def add_variations():
    Variation.objects.bulk_create(
        [
            Variation(name="size"),
            Variation(name="color"),
            Variation(name="design"),
            Variation(name="fabric"),
            Variation(name="pack"),
            Variation(name="volume"),
            Variation(name="quantity"),
            Variation(name="RAM"),
            Variation(name="memory"),
            Variation(name="weight"),
            Variation(name="dimensions"),
            Variation(name="quality"),
        ]
    )


def add_customizations():
    Customization.objects.bulk_create(
        [
            Customization(name="Print Name", description="Name to be printed"),
            Customization(name="Print Design", description="Designs to be printed"),
            Customization(name="Message", description="Message to be included"),
            Customization(name="Packaging", description="Pack together or separately"),
            Customization(name="Other", description="Other Customization"),
        ]
    )


def add_products(n):
    categories = Category.objects.all()
    sub_categories = SubCategory.objects.all()
    product_types = ProductType.objects.all()
    brands = Brand.objects.all()

    for i in range(100):
        product = Product.objects.create(
            product_type=product_types[fake.random_int(max=product_types.count() - 1)],
            name=fake.word(),
            description=fake.text(),
            category=categories[fake.random_int(max=categories.count() - 1)],
            sub_category=sub_categories[fake.random_int(max=sub_categories.count() - 1)],
            charge_taxes=fake.pybool(),
            product_qty=fake.random_int(min=10, max=1000),
            views=fake.random_int(max=10000),
            visible_in_listings=fake.pybool(),
            brand=brands[fake.random_int(max=brands.count() - 1)]
        )
        add_product_images(product)
        add_product_prices(product)
        add_product_variant(product)
        add_product_reviews(product)


def add_product_prices(product):
    n = fake.random_int(min=1, max=4)
    stores = Store.objects.all()
    ProductPrice.objects.bulk_create(
        [
            ProductPrice(
                product=product,
                min_qty=fake.random_int(min=10, max=100),
                price=fake.random_int(min=10, max=1000),
                discounted_price=fake.random_int(min=10, max=1000),
                store=stores[fake.random_int(max=stores.count() - 1)]
            )
            for _ in range(n)
        ]
    )


def add_product_images(product):
    n = fake.random_int(min=1, max=10)
    ProductImage.objects.bulk_create(
        [
            ProductImage(
                product=product,
                image=fake.image_url(),
                alt=fake.word(),
            )
            for _ in range(n)
        ]
    )


def add_product_variant(product):
    variations = Variation.objects.all()
    for i in range(fake.random_int(min=2, max=10)):
        variant = ProductVariant.objects.create(
            name=fake.word(),
            product=product,
            variant=variations[fake.random_int(max=variations.count() - 1)],
            track_inventory=fake.pybool(),
            product_qty=fake.random_int(max=1000),
            price=fake.random_int(min=10, max=10000),
            discounted_price=fake.random_int(min=10, max=10000),
        )
        add_variant_images(variant)


def add_variant_images(variant):
    images = ProductImage.objects.filter(product=variant.product)
    VariantImage.objects.bulk_create(
        [
            VariantImage(
                variant=variant,
                image=images[fake.random_int(max=images.count() - 1)]
            )
        ]
    )


def add_product_reviews(product):
    users = User.objects.all()
    ProductReview.objects.bulk_create(
        [
            ProductReview(
                user=users[fake.random_int(max=users.count() - 1)],
                product=product,
                rating=fake.random_int(max=5),
                review=fake.text()
            )
            for _ in range(fake.random_digit())

        ]
    )
    add_review_file(product)


def add_review_file(product):
    reviews = ProductReview.objects.filter(product=product)
    for i in range(reviews.count()):
        ProductReviewFile.objects.create(

            review=reviews[i],
            file=fake.file_name(extension='jpg')
        )


def add_collections():
    products = Product.objects.all()
    Collection.objects.bulk_create(
        [
            Collection(
                name=fake.word(),
                background_image=fake.image_url(),
                background_image_alt=fake.word(),
                description=fake.text(),
            )
            for i in range(10)
        ]
    )


def add_collection_products(n):
    collections = Collection.objects.all()
    products = Product.objects.all()
    CollectionProduct.objects.bulk_create(
        [
            CollectionProduct(
                collection=collections[fake.random_int(max=collections.count() - 1)],
                product=products[fake.unique.random_int(max=products.count() - 1)]
            )
            for _ in range(n)
        ]
    )


def add_brands():
    Brand.objects.bulk_create(
        [
            Brand(
                name=fake.unique.word(),
                image=fake.image_url(),
                alt=fake.word(),
                description=fake.text(),
            )
            for _ in range(20)

        ]
    )