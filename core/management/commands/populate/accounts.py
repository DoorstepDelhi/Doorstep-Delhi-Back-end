import os, django

from faker import Faker

from accounts.models import User, Address

fake = Faker()
Faker.seed(999)


def populate_users(N):
    user = User.objects.create_superuser(username='admin', password="admin")
    user = User.objects.create_superuser(username='9999999999', password="admin")
    for _ in range(2):
        add_superuser()
    for _ in range(N):
        add_user()


def add_superuser():
    username = fake.random_number(digits=10)
    first_name = fake.first_name()
    last_name = fake.last_name()
    password = fake.password(length=12)
    user = User.objects.create_superuser(username=username, first_name=first_name, last_name=last_name, password="admin")
    add_addresses(user)


def add_addresses(user):
    user = User.objects.create_user(username='8888888888', password="admin")
    user = User.objects.create_user(username='7777777777', password="admin")
    user = User.objects.create_user(username='6666666666', password="admin")
    Address.objects.bulk_create(
        [
            Address(
                user=user,
                full_name=fake.name(),
                street_address_1=fake.building_number(),
                street_address_2=fake.street_name(),
                city=fake.city(),
                state=fake.street_suffix(),
                postal_code=fake.postcode(),
                phone=fake.random_number(digits=10, fix_len=True))
            for _ in range(fake.random_int(min=2, max=10))
        ]
    )


def add_user():
    username = fake.random_number(digits=10)
    first_name = fake.first_name()
    last_name = fake.last_name()
    password = fake.password(length=12)
    user = User.objects.create_user(
        username = username,
        email=fake.email(),
        first_name=first_name,
        last_name=last_name,
        password=password,
    )
    add_addresses(user)
    addresses = Address.objects.filter(user=user)
    addresses_count = addresses.count()
    user.default_shipping_address = addresses[fake.random_int(max=addresses_count-1)]
    user.default_billing_address = addresses[fake.random_int(max=addresses_count-1)]
    user.save()
