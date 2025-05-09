# Generated by Django 5.1.7 on 2025-05-01 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_alter_album_format_color'),
        ('promotions', '0003_remove_promocode_discount_percentage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promotion',
            name='albums',
            field=models.ManyToManyField(blank=True, related_name='promotions', to='catalog.album', verbose_name='Альбомы, участвующие в акции'),
        ),
    ]
