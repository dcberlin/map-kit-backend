# Generated by Django 4.0.5 on 2023-03-21 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0006_location_locations_l_geograp_5ec53c_idx'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='community',
            options={'verbose_name_plural': 'Communities'},
        ),
    ]