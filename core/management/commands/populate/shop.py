from datetime import datetime
from django.core.checks import messages
from django.db.models.fields.files import ImageFileDescriptor
from django.utils.timezone import make_aware
from faker import Faker
import random

from room.models import Room, RoomUser
from accounts.models import User, Address
from product.models import Collection, Product, Category, ProductVariant
from shop.choices import order_status_choices, order_event_type_choices, voucher_type_choices, \
    main_order_event_type_choices
from store.models import ShippingMethod, PickupPoint
from shop.models import *

fake = Faker()
Faker.seed(999)

status_choices = []
for i in order_status_choices:
    status_choices.append(i[0])

event_type_choices = []
for i in main_order_event_type_choices:
    event_type_choices.append(i[0].upper())


def populate(total):
    populate_voucher()
    populate_giftcard()
    populate_order(50)
    populate_sale()


def populate_order(N):
    users = User.objects.all()
    addresses = Address.objects.all()
    ship_method = ShippingMethod.objects.all()
    pickup_points = PickupPoint.objects.all()
    giftcards = GiftCard.objects.filter(id=1)
    vouchers = Voucher.objects.all()
    for _ in range(N):
        order = Order.objects.create(
            created=make_aware(datetime.now()),
            status=(fake.random_element(elements=status_choices)),
            user=users[random.randint(0, users.count() - 1)],
            tracking_client_id=fake.text(max_nb_chars=20),
            billing_address=addresses[random.randint(0, addresses.count() - 1)],
            shipping_address=addresses[random.randint(0, addresses.count() - 1)],
            # pickup_point =  pickup_points[random.randint(0, pickup_points.count()-1)],
            shipping_method=ship_method[random.randint(0, ship_method.count() - 1)],
            shipping_price=fake.random_int(max=1000),
            total_net_amount=fake.random_int(max=1000),
            undiscounted_total_net_amount=fake.random_int(max=1000),
            voucher=vouchers[random.randint(0, vouchers.count() - 1)],

            # gift_cards =,
            display_gross_prices=fake.pybool(),
            customer_note=fake.text(max_nb_chars=200),
        )
        populate_invoice(order)
        populate_order_line(order)
        populate_order_event(order)
        populate_gift_cards(order)


def populate_gift_cards(order):
    giftcards = GiftCard.objects.all()
    gift_card = []
    for i in random.sample(range(giftcards.count()), random.randint(2, 5)):
        gift_card.append(giftcards[i])
    order.gift_cards.set(gift_card)
    order.save()


def populate_order_line(order):
    variants = ProductVariant.objects.all()
    OrderLine.objects.bulk_create(
        [
            OrderLine(
                order=order,
                variant=variants[random.randint(0, variants.count() - 1)],
                quantity=fake.random_int(max=100),
                quantity_fulfilled=fake.random_int(min=0, max=50),

            )

        ]
    )


def populate_order_event(order):
    users = User.objects.all()
    user = users[random.randint(0, users.count() - 1)]

    for _ in range(random.randint(2, 7)):
        OrderEvent.objects.create(

            date=make_aware(datetime.now()),
            type=fake.random_element(elements=event_type_choices),
            order=order,
            user=user,

        )


def populate_invoice(order):
    Invoice.objects.create(
        order=order,
        number=fake.text(max_nb_chars=30),
        created=order.created,
        external_url=fake.url(),
        invoice_file=fake.file_name()

    )


def populate_giftcard():
    users = User.objects.all()
    for _ in range(20):
        GiftCard.objects.bulk_create(
            [
                GiftCard(
                    code=fake.bothify(text='????-####', letters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'),
                    user=users[random.randint(0, users.count() - 1)],
                    created=fake.date_time_this_month(),
                    start_date=make_aware(datetime.now()),
                    end_date=fake.future_datetime(end_date='+30d'),
                    last_used_on=make_aware(fake.date_time_this_month()),
                    is_active=fake.pybool(),
                    initial_balance_amount=fake.random_int(min=50, max=1000),
                    current_balance_amount=fake.random_int(min=50, max=1000),
                )

            ]
        )


def populate_voucher():
    prods = Product.objects.all()
    collecs = Collection.objects.all()
    categs = Category.objects.all()
    for _ in range(30):
        Voucher.objects.bulk_create(
            [
                Voucher(
                    type=fake.random_element(elements=("entire_order", "shipping", "specific_product",)),
                    name=fake.word(),
                    value=fake.random_int(max=1000),
                    code=fake.bothify(text='????-####', letters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'),
                    usage_limit=fake.random_int(min=1, max=12),
                    used=fake.random_int(max=1000),
                    start_date=make_aware(datetime.now()),
                    end_date=make_aware(fake.future_datetime(end_date='+30d')),
                    apply_once_per_order=fake.pybool(),
                    apply_once_per_customer=fake.pybool(),
                    discount_value_type=fake.random_element(elements=("fixed", "percentage",)),
                    min_checkout_items_quantity=fake.random_int(max=10),
                )
            ]
        )


def populate_sale():
    products = Product.objects.all()
    Sale.objects.bulk_create(
        [
            Sale(
                name=fake.word(),
                type=fake.random_element(elements=("fixed", "percentage",)),
                start_date=make_aware(datetime.now()),
                end_date=make_aware(fake.future_datetime(end_date='+10d')),
            )
            for _ in range(products.count())
        ]
    )
