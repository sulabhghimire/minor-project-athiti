# Generated by Django 3.2.9 on 2021-12-29 16:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_rename_taxes_taxe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='taxe',
            old_name='service_charge',
            new_name='service_charge_percentage',
        ),
    ]