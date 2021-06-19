# Generated by Django 3.2.4 on 2021-06-19 21:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0001_initial'),
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='shop.order'),
        ),
    ]
