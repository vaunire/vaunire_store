# Generated by Django 5.1.7 on 2025-03-27 20:02

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')),
                ('order_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата получения заказа')),
                ('status', models.CharField(choices=[('new', 'Новый заказ'), ('in_progress', 'Заказ в обработке'), ('is_ready', 'Заказ готов'), ('completed', 'Заказ завершён')], default='new', max_length=20, verbose_name='Статус заказа')),
                ('buying_type', models.CharField(choices=[('self', 'Самовывоз'), ('delivery', 'Доставка')], max_length=20, verbose_name='Тип получения')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Фамилия')),
                ('phone', models.CharField(max_length=20, verbose_name='Номер телефона')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Электронная почта')),
                ('address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Адрес доставки')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Комментарий')),
                ('paid', models.BooleanField(default=False, verbose_name='Оплачен')),
                ('payment_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='ID платежа')),
                ('payment_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата оплаты')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cart.cart', verbose_name='Корзина')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='accounts.customer', verbose_name='Покупатель')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма оплаты')),
                ('payment_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='ID платежа')),
                ('payment_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата оплаты')),
                ('status', models.CharField(choices=[('pending', 'Ожидает оплаты'), ('success', 'Успешно оплачен'), ('failed', 'Ошибка оплаты')], default='pending', max_length=20, verbose_name='Статус платежа')),
                ('payment_method', models.CharField(blank=True, max_length=50, null=True, verbose_name='Способ оплаты')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='orders.order', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'Платёж',
                'verbose_name_plural': 'Платежи',
            },
        ),
    ]
