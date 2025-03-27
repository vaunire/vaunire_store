from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import RelatedDropdownFilter, RangeDateFilter, ChoicesDropdownFilter
from unfold.contrib.forms.widgets import WysiwygWidget

from orders.models import Order
from .models import Customer, Notifications

class BaseAdmin(ModelAdmin):
    list_filter_submit = True
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

class NotificationsInline(TabularInline):
    model = Notifications
    fields = ('created_at', 'text', 'is_read')
    readonly_fields = ('created_at',)
    extra = 1

class OrdersInline(TabularInline):
    model = Order
    fields = ('id', 'status', 'buying_type', 'created_at', 'cart_link', 'payment_status')
    readonly_fields = ('created_at', 'cart_link', 'payment_status')
    extra = 1
    can_delete = False

    def cart_link(self, obj):
        """Отображает ссылку на корзину заказа"""
        if obj.cart:
            url = reverse('admin:cart_cart_change', args=[obj.cart.id])
            return format_html('<a href="{}">Корзина #{}</a>', url, obj.cart.id)
        return "-"
    cart_link.short_description = 'Корзина'

    def payment_status(self, obj):
        """Отображает статус оплаты заказа"""
        if obj.paid:
            return "Оплачен"  # Если paid = True, сразу возвращаем "Оплачен"
        elif obj.payments.exists():
            payment = obj.payments.first()
            return payment.get_status_display()  # Иначе берём статус из Payment
        return "Не оплачен"
    payment_status.short_description = 'Статус оплаты'

@admin.register(Customer)
class CustomerAdmin(BaseAdmin):
    list_display = ('user', 'phone', 'email', 'is_active')
    search_fields = ('user__username', 'phone', 'email')
    list_filter = (
        'is_active',
        ('wishlist', RelatedDropdownFilter),
        ('favorite', RelatedDropdownFilter),
    )
    inlines = [NotificationsInline, OrdersInline]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user',
                'is_active',
                'phone',
                'email',
                'address',
            )
        }),
        ('Предпочтения', {
            'fields': (
                'wishlist',
                'favorite',
            ),
            'classes': ('collapse',),
        }),
    )

@admin.register(Notifications)
class NotificationsAdmin(BaseAdmin):
    list_display = ('recipient', 'created_at', 'is_read')
    search_fields = ('recipient__user__username', 'text')
    list_filter = (
        'is_read',
        ('recipient', RelatedDropdownFilter),
        ('created_at', RangeDateFilter),
    )
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'recipient',
                'created_at',
                'is_read',
            )
        }),
        ('Текст', {
            'fields': ('text',),
        }),
    )
    readonly_fields = ('created_at',)