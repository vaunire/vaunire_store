from django.db import models
from django.utils import timezone

# ❒ Модель для хранения информации о заказе пользователя
class Order(models.Model):
    # Статусы заказа
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ завершён'),
    )

    # Типы получения заказа
    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка'),
    )

    customer = models.ForeignKey('accounts.Customer', verbose_name = 'Покупатель', related_name = 'orders', on_delete = models.CASCADE)
    cart = models.ForeignKey('cart.Cart', verbose_name = 'Корзина', on_delete = models.CASCADE)
    created_at = models.DateTimeField(default = timezone.now, verbose_name = 'Дата создания заказа')
    order_date = models.DateTimeField( default = timezone.now, verbose_name = 'Дата получения заказа')

    status = models.CharField(max_length = 20, verbose_name = 'Статус заказа', choices = STATUS_CHOICES, default = STATUS_NEW)
    buying_type = models.CharField(max_length = 20, verbose_name = 'Тип получения', choices = BUYING_TYPE_CHOICES)

    first_name = models.CharField(max_length = 100, verbose_name = 'Имя', blank = True, null = True)
    last_name = models.CharField(max_length = 100, verbose_name = 'Фамилия', blank = True, null = True)
    phone = models.CharField(max_length = 20, verbose_name = 'Номер телефона')
    email = models.EmailField(verbose_name = 'Электронная почта', blank = True, null = True)
    address = models.CharField(max_length = 255, verbose_name='Адрес доставки', blank = True, null = True)
    comment = models.TextField(verbose_name = 'Комментарий', blank = True, null = True)
    paid = models.BooleanField(default = False, verbose_name = 'Оплачен')  

    def __str__(self):
        return f"Заказ №{self.id} | Покупатель: {self.customer.user.username} | Статус: {self.get_status_display()}"
    
    class Meta:
            verbose_name = 'Заказ'
            verbose_name_plural = 'Заказы'

# ❒ Модель для хранения информации о платежах по заказу
class Payment(models.Model):
    # Статусы платежа
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Ожидает оплаты'),
        (STATUS_SUCCESS, 'Успешно оплачен'),
        (STATUS_FAILED, 'Ошибка оплаты'),
    )

    order = models.ForeignKey(Order, verbose_name = 'Заказ', related_name = 'payments', on_delete = models.CASCADE)
    amount = models.DecimalField(max_digits = 10, decimal_places = 2, verbose_name = 'Сумма оплаты')
    payment_id = models.CharField(max_length = 100, verbose_name = 'ID платежа', blank = True, null = True)
    payment_date = models.DateTimeField(verbose_name = 'Дата оплаты', default = timezone.now)
    status = models.CharField(max_length = 20, verbose_name = 'Статус платежа', choices = STATUS_CHOICES, default = STATUS_PENDING)
    payment_method = models.CharField(max_length = 50, verbose_name = 'Способ оплаты', blank = True, null = True, default='Платёжная система Stripe')

    def __str__(self):
        return f"Оплата {self.payment_id} для заказа №{self.order.id} | Статус: {self.get_status_display()}"

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
