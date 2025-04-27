from django.db import models
from django.utils import timezone

from utils import upload_function

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

# ❒ Модель для хранения заявок на возврат товаров
class ReturnRequest(models.Model):
    # Статусы заявки на возврат
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'canceled'
    STATUS_PAID = 'paid'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Ожидает рассмотрения'),
        (STATUS_APPROVED, 'Одобрена'),
        (STATUS_REJECTED, 'Отменена'),
        (STATUS_PAID, 'Выплачена'),
    )

    # Причины возврата
    REASON_DEFECTIVE = 'defective'
    REASON_WRONG = 'wrong'
    REASON_NOT_NEEDED = 'not_needed'
    REASON_OTHER = 'other'

    REASON_CHOICES = (
        (REASON_DEFECTIVE, 'Товар поврежден (царапины, дефекты)'),
        (REASON_WRONG, 'Неправильный альбом / исполнитель'),
        (REASON_NOT_NEEDED, 'Товар больше не нужен'),
        (REASON_OTHER, 'Другое'),
    )

    customer = models.ForeignKey('accounts.Customer', verbose_name = 'Покупатель', related_name = 'return_requests', on_delete = models.CASCADE, blank = True, null = True)
    order = models.ForeignKey('Order', verbose_name = 'Заказ', related_name = 'return_requests', on_delete = models.CASCADE)
    products = models.ManyToManyField('cart.CartProduct', verbose_name = 'Товары для возврата', related_name = 'return_requests')
    reason = models.CharField(max_length = 50, verbose_name = 'Причина возврата', choices = REASON_CHOICES)
    details = models.TextField(verbose_name = 'Подробности', blank = True, null = True)
    file = models.FileField(upload_to = upload_function, verbose_name = 'Прикрепленный файл', blank = True, null = True)
    status = models.CharField(max_length = 20, verbose_name = 'Статус запроса', choices = STATUS_CHOICES, default = STATUS_PENDING)
    created_at = models.DateTimeField(default = timezone.now, verbose_name = 'Дата создания')
    updated_at = models.DateTimeField(auto_now = True, verbose_name = 'Дата обновления')

    def __str__(self):
        return f"Запрос на возврат для заказа №{self.order.id} | Статус: {self.get_status_display()}"

    class Meta:
        verbose_name = 'Заявка на возврат'
        verbose_name_plural = 'Заявки на возврат'
