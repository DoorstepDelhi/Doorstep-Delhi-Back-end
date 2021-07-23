from faker import Faker

from product.models import Category, Brand


fake = Faker()
Faker.seed(999)

def add_categories():
    Category.objects.bulk_create(
        [
            Category(name='Man', icon="shoe_1"),
            Category(name='Women', icon="shoe"),
            Category(name='Child', icon="baby_changing"),
            Category(name='Fourniture', icon="living_room"),
            Category(name='Watch', icon="watch"),
            Category(name='Media', icon="home_cinema"),
            Category(name='Sport', icon="sport"),
            Category(name='Travel', icon="sport"),
            Category(name='Tool', icon="tool"),
            Category(name='Game', icon="game"),
            Category(name='Home', icon="vacuum"),

        ]
    )

def add_brands():
    Brand.objects.bulk_create(
        [
            Brand(name='Wilson', image='brands/logo-03.svg', alt="Wilson", description=fake.text(), color='greenAccent'),
            Brand(name='Converse', image='brands/logo-04.svg', alt="Converse", description=fake.text(), color='cyan'),
            Brand(name='Umbro', image='brands/logo-05.svg', alt="Umbro", description=fake.text(), color='blueAccent'),
            Brand(name='Nike', image='brands/logo-06.svg', alt="Nike", description=fake.text(), color='orange'),
            Brand(name='Puma', image='brands/logo-07.svg', alt="Puma", description=fake.text(), color='pinkAccent'),
            Brand(name='Acer', image='brands/logo-08.svg', alt="Acer", description=fake.text(), color='deepPurpleAccent'),
            Brand(name='Reebook', image='brands/logo-09.svg', alt="Reebook", description=fake.text(), color='brown'),
            Brand(name='Adidas', image='brands/logo-10.svg', alt="Adidas", description=fake.text(), color='greenAccent'),
            Brand(name='Crocs', image='brands/logo-11.svg', alt="Crocs", description=fake.text(), color='redAccent'),
        ]
    )