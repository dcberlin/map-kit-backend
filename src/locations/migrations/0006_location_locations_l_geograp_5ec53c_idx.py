# Generated by Django 4.0.5 on 2022-11-19 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0005_alter_community_options_community_path_slug_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='location',
            index=models.Index(fields=['geographic_entity', 'published', 'community'], name='locations_l_geograp_5ec53c_idx'),
        ),
    ]