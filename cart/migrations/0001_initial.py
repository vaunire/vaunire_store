# Generated by Django 5.1.7 on 2025-05-22 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_products', models.IntegerField(default=0, verbose_name='Общее кол-во товара')),
                ('final_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Финальная цена')),
                ('original_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Оригинальная цена')),
                ('in_order', models.BooleanField(default=False, verbose_name='В заказе')),
                ('anonymous_user', models.BooleanField(default=False, verbose_name='Анонимный пользователь')),
            ],
            options={
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзины',
            },
        ),
        migrations.CreateModel(
            name='CartProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Количество')),
                ('final_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Общая цена')),
            ],
            options={
                'verbose_name': 'Продукт корзины',
                'verbose_name_plural': 'Продукты корзины',
            },
        ),
    ]
