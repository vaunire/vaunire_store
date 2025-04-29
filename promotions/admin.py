from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateFilter, RelatedDropdownFilter
from unfold.contrib.forms.widgets import WysiwygWidget

from .models import Promotion, PromoCode, CustomerLoyalty


class BaseAdmin(ModelAdmin):
    list_filter_submit = True
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

class PromotionAlbumInline(TabularInline):
    model = Promotion.albums.through
    fields = ('album',)
    extra = 1


class CustomerLoyaltyAlbumInline(TabularInline):
    model = CustomerLoyalty.albums.through
    fields = ('album',)
    extra = 1

@admin.register(Promotion)
class PromotionAdmin(BaseAdmin):
    list_display = ('name', 'discount_percentage', 'start_date', 'end_date', 'is_active')
    search_fields = ('name', 'description')
    list_filter = (
        ('is_active', ChoicesDropdownFilter),
        ('start_date', RangeDateFilter),
        ('end_date', RangeDateFilter),
    )
    inlines = [PromotionAlbumInline]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'name',
                'description',
                'discount_percentage',
                'is_active',
            )
        }),
        ('Даты акции', {
            'fields': (
                'start_date',
                'end_date',
            )
        }),
    )

@admin.register(PromoCode)
class PromoCodeAdmin(BaseAdmin):
    list_display = ('code', 'discount_percentage', 'discount_amount', 'valid_from', 'valid_until', 'is_active')
    search_fields = ('code',)
    list_filter = (
        ('is_active', ChoicesDropdownFilter),
        ('valid_from', RangeDateFilter),
        ('valid_until', RangeDateFilter),
    )
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'code',
                'discount_percentage',
                'discount_amount',
                'is_active',
                'min_purchase_amount',
            )
        }),
        ('Ограничения', {
            'fields': (
                'valid_from',
                'valid_until',
                'max_uses',
                'times_used',
            )
        }),
    )
    readonly_fields = ('times_used',)

@admin.register(CustomerLoyalty)
class CustomerLoyaltyAdmin(BaseAdmin):
    list_display = ('get_customer_username', 'total_amount', 'purchase_date', 'total_spent', 'discount_percentage', 'get_promocode_code', 'get_promotion_name')
    search_fields = ('customer__user__username', 'applied_promocode__code', 'applied_promotion__name')
    list_filter = (
        ('customer', RelatedDropdownFilter),
        ('applied_promocode', RelatedDropdownFilter),
        ('applied_promotion', RelatedDropdownFilter),
        ('purchase_date', RangeDateFilter),
        ('discount_percentage', ChoicesDropdownFilter),
    )
    inlines = [CustomerLoyaltyAlbumInline]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'customer',
                'total_amount',
                'purchase_date',
                'albums',
            )
        }),
        ('Накопительная система', {
            'fields': (
                'total_spent',
                'discount_percentage',
            )
        }),
        ('Примененные скидки', {
            'fields': (
                'applied_promocode',
                'applied_promotion',
            )
        }),
    )
    readonly_fields = ('purchase_date', 'total_spent', 'discount_percentage')

    def get_customer_username(self, obj):
        return obj.customer.user.username
    get_customer_username.short_description = 'Покупатель'

    def get_promocode_code(self, obj):
        return obj.applied_promocode.code if obj.applied_promocode else '-'
    get_promocode_code.short_description = 'Промокод'

    def get_promotion_name(self, obj):
        return obj.applied_promotion.name if obj.applied_promotion else '-'
    get_promotion_name.short_description = 'Акция'