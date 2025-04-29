from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe

from accounts.models import Customer, Notifications
from catalog.models import Album, PriceList

# ❒ Модель акции (например, сезонная распродажа или акция на альбомы)
class Promotion(models.Model):
    name = models.CharField(max_length = 100, verbose_name = "Наименовании акции")
    description = models.TextField(blank = True, verbose_name = "Описание")
    start_date = models.DateTimeField(verbose_name = "Дата начала")
    end_date = models.DateTimeField(verbose_name = "Дата окончания")
    discount_percentage = models.DecimalField(max_digits = 5, decimal_places = 2, validators = [MinValueValidator(0), MaxValueValidator(100)], verbose_name = "Процент скидки")
    albums = models.ManyToManyField(Album, blank = True, verbose_name = "Альбомы, участвующие в акции")
    is_active = models.BooleanField(default = True, verbose_name = "Активна")

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"

    def __str__(self):
        return f"{self.name} ({self.discount_percentage}%)"

    # Проверяет, активна ли акция по датам и статусу
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

# ❒ Модель промокода с фиксированной или процентной скидкой
class PromoCode(models.Model):
    code = models.CharField(max_length = 20, unique = True, verbose_name = "Код")
    discount_percentage = models.DecimalField(max_digits = 5, decimal_places = 2, validators = [MinValueValidator(0), MaxValueValidator(100)], default = 0, verbose_name = "Процент скидки")
    discount_amount = models.DecimalField(max_digits = 10, decimal_places = 2, validators = [MinValueValidator(0)], default = 0, verbose_name = "Фиксированная скидка (руб)")
    valid_from = models.DateTimeField(verbose_name = "Действует с")
    valid_until = models.DateTimeField(verbose_name = "Действует до")
    max_uses = models.PositiveIntegerField(default = 0, verbose_name = "Максимальное количество использований (0 = без ограничений)")
    times_used = models.PositiveIntegerField(default = 0, verbose_name = "Сколько раз использовано")
    is_active = models.BooleanField(default = True, verbose_name = "Активен")
    min_purchase_amount = models.DecimalField(max_digits = 10, decimal_places = 2, validators = [MinValueValidator(0)], default = 0, verbose_name = "Минимальная сумма покупки (руб)")

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return self.code

    # Проверяет, можно ли использовать промокод для текущей корзины
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.max_uses > 0 and self.times_used >= self.max_uses:
            return False
        return True

    # Применяет промокод к корзине и создает уведомление
    def apply_to_cart(self, cart):
        if not self.is_valid():
            if not self.is_active:
                return False, "Промокод неактивен."
            now = timezone.now()
            if now < self.valid_from or now > self.valid_until:
                return False, "Промокод истек или еще не действует."
            if self.max_uses > 0 and self.times_used >= self.max_uses:
                return False, "Промокод достиг лимита использований."
            if cart.final_price < self.min_purchase_amount:
                return False, f"Сумма корзины должна быть не менее {self.min_purchase_amount} ₽."
            if self.discount_percentage > 0:
                discount = cart.final_price * (self.discount_percentage / Decimal('100.00'))
                cart.final_price -= discount
        elif self.discount_amount > 0:
            cart.final_price -= self.discount_amount
        if cart.final_price < 0:
            cart.final_price = Decimal('0.00')
        self.times_used += 1
        self.save()
        return True, ""

        messages.success(request, f'Промокод "{self.code}" успешно применен! ' \
                                  f'Скидка: {self.discount_percentage}% или {self.discount_amount} руб.')

# ❒ Модель для хранения истории покупок и накопительных скидок клиента
class CustomerLoyalty(models.Model):
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = "loyalty_records")
    total_amount = models.DecimalField(max_digits = 10, decimal_places = 2, validators = [MinValueValidator(0)], verbose_name = "Сумма покупки")
    purchase_date = models.DateTimeField(auto_now_add = True)
    applied_promocode = models.ForeignKey('PromoCode', on_delete = models.SET_NULL, null = True, blank = True)
    applied_promotion = models.ForeignKey('Promotion', on_delete = models.SET_NULL, null = True, blank = True)
    albums = models.ManyToManyField(Album)
    total_spent = models.DecimalField(max_digits = 12, decimal_places = 2, default = 0, validators = [MinValueValidator(0)], verbose_name = "Общая сумма покупок")
    discount_percentage = models.DecimalField(max_digits = 5, decimal_places = 2, default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)], verbose_name = "Накопительная скидка (%)")

    class Meta:
        verbose_name = "Программа лояльности"
        verbose_name_plural = "Программы лояльности"
        ordering = ['-purchase_date']

    def __str__(self):
        return f"{self.customer.user.username}: {self.total_spent} руб. (Скидка: {self.discount_percentage}%)"

    def update_discount(self):
        """Обновляет процент скидки на основе общей суммы покупок"""
        if self.total_spent >= Decimal('30000'): self.discount_percentage = Decimal('5.00')
        elif self.total_spent >= Decimal('10000'): self.discount_percentage = Decimal('2.00')
        else: self.discount_percentage = Decimal('0.00')
        self.save()