from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models

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
    fields = ('cart_product_id', 'divider', 'display_name', 'quantity', 'final_price')
    readonly_fields = ('display_name', 'cart_product_id', 'divider')  
    extra = 1

    def divider(self, obj):
        return ":"
    divider.short_description = ''

    def cart_product_id(self, obj):
        return obj.id if obj.id else '-' 
    cart_product_id.short_description = 'ID'

    def display_name(self, obj):
        return obj.display_name
    display_name.short_description = 'Товар'

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