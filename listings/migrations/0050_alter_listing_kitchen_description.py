# Generated by Django 3.2.9 on 2022-01-29 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0049_auto_20220127_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='kitchen_description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
