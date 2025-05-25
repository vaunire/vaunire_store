from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (MultipleRelatedDropdownFilter,
                                          RelatedDropdownFilter)
from unfold.contrib.forms.widgets import WysiwygWidget

from .models import Cart, CartProduct

class BaseAdmin(ModelAdmin):
    list_filter_submit = True  
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},  
    }

class CartProductInline(TabularInline):
    model = CartProduct
    fields = ('display_name', 'price_list_link', 'original_price', 'divider', 'quantity', 'final_price')
    readonly_fields = ('price_list_link', 'display_name', 'divider', 'original_price')  
    extra = 0

    def divider(self, obj):
        return ":"
    divider.short_description = ''

    def display_name(self, obj):
        return obj.display_name
    display_name.short_description = 'Товар'

    def price_list_link(self, obj):
        """Отображает ссылку на активный прайс-лист, связанный с альбомом"""
        if obj.content_object and obj.content_type.model == 'album':
            price_list_item = obj.content_object.items.filter(price_list__is_active=True).first()
            if price_list_item:
                url = reverse('admin:catalog_pricelist_change', args=[price_list_item.price_list.id])
                return format_html('<a href="{}" style="text-decoration: underline;">Нажмите, чтобы перейти</a>', url)
        return "-"  
    price_list_link.short_description = 'Прайс - лист'


    def original_price(self, obj):
        """Возвращает оригинальную цену альбома из активного прайс-листа"""
        if obj.content_object and obj.content_type.model == 'album':
            price_list_item = obj.content_object.items.filter(price_list__is_active=True).first()
            if price_list_item:
                return f"{price_list_item.price:.2f}"
        return "-"
    original_price.short_description = 'Цена за ед.'

@admin.register(Cart)
class CartAdmin(BaseAdmin):
    list_display = ('id', 'owner', 'total_products', 'final_price', 'in_order', 'anonymous_user')
    search_fields = ('id', 'owner__user__username') 
    list_filter = (
        ('owner', RelatedDropdownFilter), 
        'in_order',  
        'anonymous_user',  
    )
    inlines = [CartProductInline]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'owner',
                'in_order',
                'anonymous_user',
            )
        }),
        ('Итоги', {
            'fields': (
                'total_products',
                'final_price',
            ),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('total_products', 'final_price')

    def total_products(self, obj):
        return obj.total_products
    total_products.short_description = 'Количество товаров'

    def final_price(self, obj):
        return f"{obj.final_price} ₽"
    final_price.short_description = 'Итоговая цена'

@admin.register(CartProduct)
class CartProductAdmin(BaseAdmin):
    list_display = ('display_name', 'cart', 'quantity', 'final_price')
    search_fields = ('cart__id', 'content_object__name')  
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user',
                'cart',
                'content_type',
                'object_id',
            )
        }),
        ('Детали', {
            'fields': (
                'quantity',
                'final_price',
            )
        }),
    )
    readonly_fields = ('final_price',)  

    def display_name(self, obj):
        return obj.display_name
    display_name.short_description = 'Продукт'