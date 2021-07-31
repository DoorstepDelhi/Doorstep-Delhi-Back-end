from datetime import datetime
from django.core.checks import messages
from django.db.models.fields.files import ImageFileDescriptor
from django.utils.timezone import make_aware
from faker import Faker
import random

from room.models import Room, RoomUser
from accounts.models import User, Address
from product.models import Product, ProductVariant
from room.models import *
from shop.choices import order_status_choices, order_event_type_choices
from store.models import ShippingMethod

fake = Faker()
Faker.seed(999)

status_choices = []
for i in order_status_choices:
    status_choices.append(i[0])

event_type_choices = []
for i in order_event_type_choices:
    event_type_choices.append(i[0].upper())


def populate(n):
    populate_room(n)


def populate_room(n):
    for i in range(n):
        room = Room.objects.create(
            name=fake.word(),
            title=fake.text(max_nb_chars=25),
            description=fake.paragraph(nb_sentences=5),
            image=f'rooms/({fake.random_int(min=1, max=150)}).jpg',
            created_at=fake.date_time_this_month()
        )
        populate_room_users(room)
        populate_room_wishlist_product(room)
        populate_room_order(room)
        populate_message(room)


def populate_room_users(room):
    users = User.objects.all()
    RoomUser.objects.bulk_create(
        [
            RoomUser(
                room=room,
                user=users[i],
                role=fake.random_element(elements=('A', 'U')),
                joined_at=fake.date_time_this_month()
            )
            for i in random.sample(
            range(users.count()),
            fake.random_int(min=2, max=min(users.count(), 50))
        )
        ]
    )
    report_group(room)


def populate_room_wishlist_product(room):
    users = room.users.all()
    products = Product.objects.all()

    for i in random.sample(
            range(products.count()),
            fake.random_int(min=2, max=min(products.count(), 10))
    ):
        wishlist_item = RoomWishlistProduct.objects.create(
            room=room,
            user=users[fake.random_int(min=min(0, users.count() - 1), max=min(100, users.count() - 1))],
            product=products[i],
            added_at=fake.date_time_this_month(),
            votes=fake.random_int(max=users.count()),
        )
        # populate_wishlist_product_vote(wishlist_item)


def populate_wishlist_product_vote(wishlist_item):
    users = wishlist_item.room.users.all()
    WishlistProductVote.objects.bulk_create(
        [
            WishlistProductVote(
                product=wishlist_item,
                user=users[j]
            )
            for j in random.sample(range(users.count()), min(users.count(), wishlist_item.votes))
        ]
    )


def populate_room_order(room):
    users = room.users.all()
    addresses = Address.objects.all()
    ship_method = ShippingMethod.objects.all()
    for _ in range(fake.random_int(min=3, max=20)):
        room_order = RoomOrder.objects.create(
            room=room,
            created=make_aware(datetime.now()),
            status=(fake.random_element(elements=status_choices)),
            tracking_client_id=fake.text(max_nb_chars=20),
            billing_address=addresses[random.randint(0, addresses.count() - 1)],
            shipping_address=addresses[random.randint(0, addresses.count() - 1)],
            shipping_method=ship_method[random.randint(0, ship_method.count() - 1)],
            shipping_price=fake.random_int(max=1000),
            total_net_amount=fake.random_int(max=1000),
            undiscounted_total_net_amount=fake.random_int(max=1000)
        )
        populate_room_order_line(room, room_order)


def populate_room_order_line(room, room_order):
    users = room.users.all()
    products = Product.objects.all()

    for j in random.sample(range(products.count()),
                           fake.random_int(min=min(products.count(), 1), max=min(products.count(), 10))):
        room_order_line = RoomOrderLine.objects.create(
            order=room_order,
            user=users[random.randint(0, users.count() - 1)],
            product=products[j],
            status=room_order.status,
            created_at=room_order.created
        )
        populate_order_line_variant(room_order_line)
        populate_invoice(room_order)


def populate_order_line_variant(order_line):
    variants = ProductVariant.objects.filter(product=order_line.product)
    for _ in range(fake.random_int(min=1, max=5)):
        order_line_variants = RoomOrderLineVariant.objects.create(
            order_line=order_line,
        )
        for i in random.sample(
                range(variants.count()),
                fake.random_int(min=1, max=min(variants.count(), 4))
        ):
            order_line_variants.variants.add(variants[i])
        populate_user_order_line(order_line_variants)


def populate_user_order_line(order_line_variants):
    users = order_line_variants.order_line.order.room.users.all()

    UserOrderLine.objects.bulk_create(
        [
            UserOrderLine(
                user=users[i],
                product=order_line_variants,
                quantity=fake.random_int(max=100),
                quantity_fulfilled=fake.random_int(min=0, max=50),
                # quantity fulfilled might be greater than quantity of product
                updated_at=make_aware(datetime.now()),
                customization=fake.text(max_nb_chars=200),
                file=fake.file_name()
            )
            for i in random.sample(range(users.count()),
                                   fake.random_int(min=min(users.count(), 1), max=min(users.count(), 10)))
        ]
    )


# def populate_order_event(room):
#     orders = RoomOrder.objects.filter(room = room)
#     users = User
#     for i in range(orders.count()):
#         OrderEvent.objects.bulk_create(
#         [
#             OrderEvent(
#                 date = make_aware(date.now()),
#                 type = (fake.random_element(elements=event_type_choices)),
#                 order = orders[i],
#                 user =
#             )

#         ]
#     )


def populate_invoice(roomorder):
    Invoice.objects.create(
        order=roomorder,
        number=fake.text(max_nb_chars=30),
        created=roomorder.created,
        external_url=fake.url(),
        invoice_file=fake.file_name()

    )


def populate_message(room):
    users = room.users.all()
    products = Product.objects.all()
    Message.objects.bulk_create(
        [
            Message(
                file_field=fake.file_name(),
                message_text=fake.text(max_nb_chars=75),
                product=products[random.randint(0, products.count() - 1)],
                user=users[fake.random_int(min=0, max=users.count() - 1)],
                created_on=make_aware(datetime.now()),
                room=room
            )
            for _ in range(fake.random_int(min=5, max=10))
        ]
    )


def report_group(room):
    users = room.users.all()
    ReportGroup.objects.bulk_create(
        [
            ReportGroup(
                user=users[fake.random_int(min=0, max=users.count() - 1)],
                room=room,
                date_time=make_aware(datetime.now())
            )
            for _ in range(fake.random_int(min=0, max=min(2, users.count() - 1)))
        ]
    )
