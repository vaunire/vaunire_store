from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# operator — модуль для динамической работы с атрибутами объектов, нужен для attrgetter
import operator


# ❒ Модель для хранения корзины пользователя
class Cart(models.Model):
    owner = models.ForeignKey('accounts.Customer', verbose_name = 'Покупатель', on_delete = models.CASCADE)
    products = models.ManyToManyField('CartProduct', blank = True, verbose_name = 'Продукты для корзины', related_name = 'related_cart')
    total_products = models.IntegerField(default = 0, verbose_name = 'Общее кол-во товара')
    final_price = models.DecimalField(max_digits = 10, decimal_places = 2, verbose_name = 'Общая цена', null = True, blank = True)
    in_order = models.BooleanField(default = False, verbose_name = 'В заказе')
    anonymous_user = models.BooleanField(default = False, verbose_name = 'Анонимный пользователь')

    def __str__(self):
        return str(self.id)

    class Meta:
            verbose_name = 'Корзина'
            verbose_name_plural = 'Корзины'

    def update_totals(self):
        # Обновляет общее количество и итоговую цену корзины
        cart_products = self.products.all()
        self.total_products = cart_products.count()
        self.final_price = sum(cp.final_price for cp in cart_products) or 0
        self.save(update_fields=['total_products', 'final_price'])

    def save(self, *args, **kwargs):
        # Пересчитывает итоги после сохранения корзины
        super().save(*args, **kwargs)
        self.update_totals()

    @property
    # Возвращает список объектов (например, Album), находящихся в корзине.
    def products_in_cart(self):
        return [cart_product.content_object for cart_product in self.products.all()]

# ❒ Промежуточная модель для хранения товаров в корзине
class CartProduct(models.Model):
    # Если магазин расширится и начнет продавать не только альбомы, но и, например, услуги, модель CartProduct можно легко адаптировать:
    MODEL_CART_PRODUCT_DISPLAY_NAME_MAP = {
         "Album" : {"is_constructable": True, "fields": ["name", "artist.name"], "separator": ' - '}
         # "Service": {"is_constructable": False, "field": "name"},
         # "RecordPlayer": {"is_constructable": True, "fields": ["brand", "model"], "separator": ' '},
    }

    user = models.ForeignKey('accounts.Customer', verbose_name = 'Покупатель', on_delete = models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name = 'Корзина', on_delete = models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete = models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField(default = 1)
    final_price = models.DecimalField(max_digits = 10, decimal_places = 2, verbose_name = 'Общая цена')

    def __str__(self):
        return f"Продукт: {self.content_object.name} (для корзины)"

    def get_product_price(self):
        # Возвращает текущую цену продукта из прайс-листа для Album
        if self.content_type.model == 'album': 
            return self.content_object.current_price  
        # elif self.content_type.model == 'service':
        #     return self.content_object.price
        raise ValueError(f"Объект {self.content_object} не поддерживает определение цены")

    @property
    # Возвращает отображаемое имя продукта в корзине
    def display_name(self):
        model_fields = self.MODEL_CART_PRODUCT_DISPLAY_NAME_MAP.get(self.content_object.__class__._meta.model_name.capitalize())
        # Если is_constructable равно True, имя формируется динамически из указанных полей
        if model_fields and model_fields['is_constructable']:
            display_name = model_fields['separator'].join(
                # operator.attrgetter — извлекает атрибуты (например, name, artist.name) динамически из content_object
                [operator.attrgetter(field)(self.content_object) for field in model_fields['fields']]
            )
            return display_name
        # Если is_constructable равно False, имя берется напрямую из указанного поля
        if model_fields and not model_fields['is_constructable']:
            display_name = operator.attrgetter(model_fields['field'])(self.content_object)
            return display_name
        return self.content_object
    
    def save(self, *args, **kwargs):
        # Пересчитывает итоговую цену на основе текущей цены продукта из прайс-листа
        self.final_price = self.quantity * self.get_product_price()
        super().save(*args, **kwargs)

    class Meta:
            verbose_name = 'Продукт корзины'
            verbose_name_plural = 'Продукты корзины'

