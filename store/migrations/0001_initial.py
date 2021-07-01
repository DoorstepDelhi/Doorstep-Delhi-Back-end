# Generated by Django 3.2.4 on 2021-07-01 18:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ShippingZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('countries', django_countries.fields.CountryField(blank=True, default=[], max_length=746, multiple=True)),
                ('default', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='stores')),
                ('website', models.URLField(null=True)),
                ('facebook_link', models.URLField(null=True)),
                ('instagram_link', models.URLField(null=True)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.address')),
                ('shipping_zones', models.ManyToManyField(to='store.ShippingZone')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ShippingMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('S', 'Free Shipping'), ('FS', 'Fast Shipping'), ('DS', 'Default Shipping')], max_length=30)),
                ('maximum_delivery_days', models.PositiveIntegerField(blank=True, null=True)),
                ('minimum_delivery_days', models.PositiveIntegerField(blank=True, null=True)),
                ('excluded_products', models.ManyToManyField(blank=True, to='product.Product')),
                ('shipping_zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipping_methods', to='store.shippingzone')),
            ],
        ),
        migrations.CreateModel(
            name='PickupPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('user_aadhaar', models.CharField(max_length=12)),
                ('opening_time', models.TimeField()),
                ('closing_time', models.TimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('holder_name', models.CharField(max_length=128)),
                ('account_number', models.CharField(max_length=18)),
                ('ifsc', models.CharField(max_length=12)),
                ('account_type', models.CharField(choices=[('S', 'Savings'), ('C', 'Current')], max_length=1)),
                ('bank_name', models.CharField(max_length=128)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.store')),
            ],
        ),
    ]
