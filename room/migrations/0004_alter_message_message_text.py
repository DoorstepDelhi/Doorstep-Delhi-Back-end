# Generated by Django 3.2.4 on 2021-07-22 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0003_message_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='message_text',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
