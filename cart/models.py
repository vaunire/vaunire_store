from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from decimal import Decimal

from promotions.models import PromoCode

# operator — модуль для динамической работы с атрибутами объектов, нужен для attrgetter
import operator


# ❒ Модель для хранения корзины пользователя
class Cart(models.Model):
    owner = models.ForeignKey('accounts.Customer', verbose_name = 'Покупатель', on_delete = models.CASCADE)
    total_products = models.IntegerField(default = 0, verbose_name = 'Общее кол-во товара')
    final_price = models.DecimalField(max_digits = 10, decimal_places = 2, verbose_name = 'Финальная цена', null = True, blank = True)
    original_price = models.DecimalField(max_digits = 10, decimal_places = 2, verbose_name = 'Оригинальная цена', null = True, blank = True)
    applied_promocode = models.ForeignKey(PromoCode, verbose_name = 'Примененный промокод', null = True, blank = True, on_delete = models.SET_NULL)
    in_order = models.BooleanField(default = False, verbose_name = 'В заказе')
    anonymous_user = models.BooleanField(default = False, verbose_name = 'Анонимный пользователь')

    def __str__(self):
        return str(self.id)

    class Meta:
            verbose_name = 'Корзина'
            verbose_name_plural = 'Корзины'

    def update_totals(self):

        if not self.pk:  # Если объект еще не сохранен
            self.original_price = 0
            self.final_price = 0
            self.action_discount = 0
            self.promocode_discount = 0
            return

        cart_products = self.products.all()
        self.total_products = sum(cp.quantity for cp in cart_products) or 0
        # Рассчитываем оригинальную цену (без скидок)
        self.original_price = sum(cp.quantity * cp.content_object.current_price for cp in cart_products) or Decimal('0.00')
        # Рассчитываем финальную цену (с учетом акций)
        self.final_price = sum(cp.quantity * cp.content_object.discounted_price for cp in cart_products) or Decimal('0.00')

        # Применяем промокод
        if self.applied_promocode:
            success, message = self.applied_promocode.apply_to_cart(self)
            if not success:
                self.applied_promocode = None  # Сбрасываем промокод, если он невалиден

        if self.final_price < 0:
            self.final_price = Decimal('0.00')

    def save(self, *args, **kwargs):
        if not self.pk:  # Если объект новый, сначала сохранить
            super().save(*args, **kwargs)  # Сохраняем, чтобы получить pk
        self.update_totals()
        super().save(*args, **kwargs)  # Сохраняем с обновленными totals

    @property
    # Возвращает список объектов (например, Album), находящихся в корзине.
    def products_in_cart(self):
        return [cart_product.content_object for cart_product in self.products.all()]

    @property
    def discount(self):
        if self.original_price > self.final_price:
            return self.original_price - self.final_price
        return 0

# ❒ Промежуточная модель для хранения товаров в корзине
class CartProduct(models.Model):
    # Если магазин расширится и начнет продавать не только альбомы, но и, например, услуги, модель CartProduct можно легко адаптировать:
    MODEL_CART_PRODUCT_DISPLAY_NAME_MAP = {
         "Album" : {"is_constructable": True, "fields": ["name", "artist.name"], "separator": ' - '}
         # "Service": {"is_constructable": False, "field": "name"},
         # "RecordPlayer": {"is_constructable": True, "fields": ["brand", "model"], "separator": ' '},
    }

    user = models.ForeignKey('accounts.Customer', verbose_name = 'Покупатель', on_delete = models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name = 'Корзина', on_delete = models.CASCADE, related_name = 'products')

    content_type = models.ForeignKey(ContentType, on_delete = models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField(default = 1, verbose_name = 'Количество')
    final_price = models.DecimalField(max_digits = 10, decimal_places = 2, verbose_name = 'Общая цена')

    def __str__(self):
        return f"Продукт: {self.content_object.name}"
        
    def get_product_price(self):
        # Возвращает текущую цену продукта из прайс-листа для Album
        if self.content_type.model == 'album': 
            return self.content_object.discounted_price  
        # elif self.content_type.model == 'service':
        #     return self.content_object.price
        raise ValueError(f"Объект {self.content_object} не поддерживает определение цены")

    @property
    # Возвращает отображаемое имя продукта в корзине
    def display_name(self):
        model_fields = self.MODEL_CART_PRODUCT_DISPLAY_NAME_MAP.get(self.content_object.__class__._meta.model_name.capitalize())
        prefix = model_fields.get("prefix", "")
        # Если is_constructable равно True, имя формируется динамически из указанных полей
        if model_fields and model_fields['is_constructable']:
            display_name = model_fields['separator'].join(
                # operator.attrgetter — извлекает атрибуты (например, name, artist.name) динамически из content_object
                [operator.attrgetter(field)(self.content_object) for field in model_fields['fields']]
            )
            return f"{prefix}{display_name}"
        # Если is_constructable равно False, имя берется напрямую из указанного поля
        if model_fields and not model_fields['is_constructable']:
            display_name = operator.attrgetter(model_fields['field'])(self.content_object)
            return f"{prefix}{display_name}"
        return self.content_object
    
    def save(self, *args, **kwargs):
        # Пересчитывает итоговую цену на основе текущей цены продукта из прайс-листа
        self.final_price = self.quantity * self.get_product_price()
        super().save(*args, **kwargs)
        self.cart.save()

    class Meta:
            verbose_name = 'Продукт корзины'
            verbose_name_plural = 'Продукты корзины'
            unique_together = [['cart', 'content_type', 'object_id']]

