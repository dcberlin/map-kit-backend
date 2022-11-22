# Generated by Django 4.0.5 on 2022-06-30 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0004_category_color'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='community',
            options={},
        ),
        migrations.AddField(
            model_name='community',
            name='path_slug',
            field=models.SlugField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='community',
            name='name',
            field=models.CharField(default='<placeholder>', max_length=128),
            preserve_default=False,
        ),
    ]