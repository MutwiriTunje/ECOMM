# Generated by Django 5.0.7 on 2024-07-27 16:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_customer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='state',
            new_name='county',
        ),
    ]