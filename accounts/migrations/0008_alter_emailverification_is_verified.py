# Generated by Django 3.2.9 on 2022-02-13 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_emailverification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverification',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
