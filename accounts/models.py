from django.db import models

from django.conf import settings  
from django.utils import timezone 

from catalog.models import Album, check_stock_change

# pre_save — проверяем изменения перед сохранением объекта, post_save — сигнал, который срабатывает после сохранения объекта; оба используются для уведомлений.
from django.db.models.signals import post_save, pre_save
from django.utils.safestring import mark_safe


 # ❒ Модель для хранения информации о покупателе
class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name = 'Пользователь', on_delete = models.CASCADE)
    is_active = models.BooleanField(default = True, verbose_name = 'Пользователь активен')

    wishlist = models.ManyToManyField('catalog.Album', verbose_name = 'Список ожидания', blank = True)
    favorite = models.ManyToManyField('catalog.Album', verbose_name = 'Понравившиеся альбомы', blank = True, related_name = 'favorited_by')

    phone = models.CharField(max_length = 20, verbose_name = 'Номер телефона')
    email = models.EmailField(verbose_name = 'Электронная почта', blank = True, null = True)
    address = models.CharField(max_length = 255, verbose_name='Адрес доставки', blank = True, null = True)

    def __str__(self):
            return f"{self.user.username}"
    
    class Meta:
            verbose_name = 'Покупатель'
            verbose_name_plural = 'Покупатели'

# ❒ Кастомный менеджер для работы с уведомлениями
class NotificationManager(models.Manager):

    # Возвращает базовый QuerySet для модели уведомлений
    def get_queryset(self):
        return super().get_queryset()

    # Возвращает все непрочитанные уведомления для указанного получателя
    def unread_for_recipient(self, recipient):
        return self.get_queryset().filter(
            recipient = recipient,
            is_read = False
        )

    # Помечает все непрочитанные уведомления для указанного получателя как прочитанные
    def mark_unread_as_read(self, recipient):
        qs = self.get_queryset().filter(
            recipient = recipient,
            is_read = False
        )
        qs.update(is_read = True)

# ❒ Модель для хранения уведомлений, отправляемых пользователям
class Notifications(models.Model):
    recipient = models.ForeignKey(Customer, verbose_name = 'Получатель', related_name = 'notifications', on_delete = models.CASCADE)
    created_at = models.DateTimeField(verbose_name = 'Дата создания', default = timezone.now)
    text = models.TextField(verbose_name = 'Текст уведомления')
    is_read = models.BooleanField(default = False, verbose_name = 'Прочитано')
    objects = NotificationManager()

    def __str__(self):
            return f"Уведомление для {self.recipient.user.username} | id = {self.id}"
    
    class Meta:
            verbose_name = 'Уведомление'
            verbose_name_plural = 'Уведомления'
            ordering = ['-created_at'] 

def send_notification(instance, **kwargs):
    # Отправляет уведомления клиентам, которые добавили альбом в лист ожидания, если альбом появился в наличии
    if instance.stock and instance.out_of_stock:
        # Ищем всех клиентов, у которых этот альбом в списке ожидания (wishlist)
        customers = Customer.objects.filter(
            wishlist__in = [instance]
        )
        if customers.count():
            for customer in customers:
                Notifications.objects.create(
                    recipient = customer,
                    text = mark_safe(f'Альбом <a href="{instance.get_absolute_url()}">"{instance.name}"</a>, '
                                     f'который Вы ожидаете, теперь доступен для приобретения!')
                )
                customer.wishlist.remove(instance)
post_save.connect(send_notification, sender = Album)
pre_save.connect(check_stock_change, sender = Album)