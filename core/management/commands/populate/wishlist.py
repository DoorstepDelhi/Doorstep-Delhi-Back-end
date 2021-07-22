from faker import Faker
import random

from accounts.models import User
from product.models import Product
from wishlist.models import Wishlist, WishlistItem


fake = Faker()
Faker.seed(999)


def populate_wishlist():
    users = User.objects.all()
    products = Product.objects.all()

    for user in users:
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        for i in random.sample(
                range(products.count()),
                fake.random_int(min=2, max=min(products.count(), 10))
        ):
            WishlistItem.objects.bulk_create(
                [
                    WishlistItem(
                        wishlist=wishlist,
                        product=products[fake.random_int(min=min(0, products.count() - 1), max=min(20, products.count() - 1))],
                    )
                ]
            )
