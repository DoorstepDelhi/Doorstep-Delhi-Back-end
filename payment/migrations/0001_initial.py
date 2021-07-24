# Generated by Django 3.2.5 on 2021-07-24 03:01

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gateway', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('to_confirm', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('charge_status', models.CharField(choices=[('not-charged', 'Not charged'), ('pending', 'Pending'), ('partially-charged', 'Partially charged'), ('fully-charged', 'Fully charged'), ('partially-refunded', 'Partially refunded'), ('fully-refunded', 'Fully refunded'), ('refused', 'Refused'), ('cancelled', 'Cancelled')], default='not-charged', max_length=20)),
                ('total', models.DecimalField(decimal_places=3, default=Decimal('0.0'), max_digits=12)),
                ('captured_amount', models.DecimalField(decimal_places=3, default=Decimal('0.0'), max_digits=12)),
                ('billing_email', models.EmailField(blank=True, max_length=254)),
                ('billing_first_name', models.CharField(blank=True, max_length=256)),
                ('billing_last_name', models.CharField(blank=True, max_length=256)),
                ('billing_company_name', models.CharField(blank=True, max_length=256)),
                ('billing_address_1', models.CharField(blank=True, max_length=256)),
                ('billing_address_2', models.CharField(blank=True, max_length=256)),
                ('billing_city', models.CharField(blank=True, max_length=256)),
                ('billing_city_area', models.CharField(blank=True, max_length=128)),
                ('billing_postal_code', models.CharField(blank=True, max_length=256)),
                ('billing_country_code', models.CharField(blank=True, max_length=2)),
                ('billing_country_area', models.CharField(blank=True, max_length=256)),
                ('cc_first_digits', models.CharField(blank=True, default='', max_length=6)),
                ('cc_last_digits', models.CharField(blank=True, default='', max_length=4)),
                ('cc_brand', models.CharField(blank=True, default='', max_length=40)),
                ('cc_exp_month', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)])),
                ('cc_exp_year', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1000)])),
                ('payment_method_type', models.CharField(blank=True, max_length=256)),
                ('customer_ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('extra_data', models.TextField(blank=True, default='')),
                ('return_url', models.URLField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Payment',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('kind', models.CharField(choices=[('external', 'External reference'), ('auth', 'Authorization'), ('pending', 'Pending'), ('action_to_confirm', 'Action to confirm'), ('refund', 'Refund'), ('refund_ongoing', 'Refund in progress'), ('capture', 'Capture'), ('void', 'Void'), ('confirm', 'Confirm'), ('cancel', 'Cancel')], max_length=25)),
                ('is_success', models.BooleanField(default=False)),
                ('action_required', models.BooleanField(default=False)),
                ('action_required_data', models.TextField()),
                ('amount', models.DecimalField(decimal_places=3, default=Decimal('0.0'), max_digits=12)),
                ('error', models.CharField(choices=[('incorrect_number', 'incorrect_number'), ('invalid_number', 'invalid_number'), ('incorrect_cvv', 'incorrect_cvv'), ('invalid_cvv', 'invalid_cvv'), ('incorrect_zip', 'incorrect_zip'), ('incorrect_address', 'incorrect_address'), ('invalid_expiry_date', 'invalid_expiry_date'), ('expired', 'expired'), ('processing_error', 'processing_error'), ('declined', 'declined')], max_length=256, null=True)),
                ('customer_id', models.CharField(max_length=256, null=True)),
                ('gateway_response', models.TextField()),
                ('already_processed', models.BooleanField(default=False)),
                ('checksum', models.CharField(blank=True, max_length=100, null=True)),
                ('searchable_key', models.CharField(blank=True, max_length=512, null=True)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='payment.payment')),
            ],
        ),
    ]
