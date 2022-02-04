# Generated by Django 3.2.9 on 2022-02-04 04:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_user_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.PositiveIntegerField(blank=True, default=0, error_messages={'required': 'Enter a valid phone number'}, unique=True, validators=[django.core.validators.MaxValueValidator(9999999999), django.core.validators.MinValueValidator(9000000000)]),
        ),
    ]
