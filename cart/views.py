from decimal import Decimal

from django import views
from django.contrib import messages
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render

from catalog.models import Album
from accounts.mixins import NotificationsMixin
from orders.forms import OrderForm
from orders.models import Order, ReturnRequest
from promotions.models import PromoCode

from .models import Cart, CartProduct
from .mixins import CartMixin

class CartView(CartMixin, NotificationsMixin, views.View):
    """Отображает страницу корзины пользователя"""
    def get(self, request, *args, **kwargs):
        context = {
            'cart': self.cart,
            'notifications': self.notifications(request.user)
        }
        return render(request, 'pages/cart.html', context)

class AddToCartView(CartMixin, views.View):
    """Добавляет товар в корзину и обновляет её итоги"""
    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model = ct_model)
        product = content_type.model_class().objects.get(slug = product_slug)
        # Проверяем, есть ли уже такой продукт в корзине
        cart_product, created = CartProduct.objects.get_or_create(
            user = self.cart.owner,
            cart = self.cart,
            content_type = content_type,
            object_id = product.id,
            defaults={'quantity': 1}
        )

        if not created:
            cart_product.quantity += 1
        cart_product.save() 

        self.cart.update_totals()
        self.cart.save()

        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class RemoveFromCartView(CartMixin, views.View):
    """Удаляет товар из корзины и обновляет её итоги"""
    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model = ct_model)
        product = content_type.model_class().objects.get(slug = product_slug)

        cart_product = CartProduct.objects.filter(
            user = self.cart.owner,
            cart = self.cart,
            content_type = content_type,
            object_id = product.id
        ).first()

        cart_product.delete()
        self.cart.update_totals()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class ChangeQuantityView(CartMixin, views.View):
    """Обновляет количество товара в корзине и пересчитывает итоги"""
    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model = ct_model)
        product = content_type.model_class().objects.get(slug = product_slug)

        cart_product = CartProduct.objects.filter(
            user = self.cart.owner,
            cart = self.cart,
            content_type = content_type,
            object_id = product.id
        ).first()

        if not cart_product:
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        action = request.POST.get('action')
        current_quantity = int(request.POST.get('current_quantity', cart_product.quantity))

        if action == 'decrease':
            new_quantity = current_quantity - 1
        elif action == 'increase':
            new_quantity = current_quantity + 1
        else:
            new_quantity = current_quantity

        if new_quantity < 1:
            cart_product.delete()
        else:
            cart_product.quantity = new_quantity
            cart_product.save()

        self.cart.update_totals()
        self.cart.save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class ClearCartView(CartMixin, views.View):
    """Очищает корзину пользователя"""
    def get(self, request, *args, **kwargs):
        CartProduct.objects.filter(cart = self.cart).delete()
        self.cart.applied_promocode = None 
        self.cart.update_totals()
        self.cart.save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class ApplyPromoCodeView(CartMixin, views.View):
    """Применяет промокод к корзине"""
    def post(self, request, *args, **kwargs):
        if not self.cart:
            messages.error(request, 'Корзина пуста или недоступна.')
            return HttpResponseRedirect(reverse('cart'))

        code = request.POST.get('promo_code')
        if not code:
            messages.error(request, 'Введите промокод.')
            return HttpResponseRedirect(reverse('cart'))

        try:
            promocode = PromoCode.objects.get(code=code)
            success, error_message = promocode.apply_to_cart(self.cart)
            if success:
                self.cart.applied_promocode = promocode
                self.cart.save()
                messages.success(request, f'Промокод "{promocode.code}" успешно применен!')
            else:
                messages.error(request, error_message or 'Промокод недействителен или не применим.')
            return HttpResponseRedirect(reverse('cart'))
        except PromoCode.DoesNotExist:
            messages.error(request, 'Промокод не найден.')
            return HttpResponseRedirect(reverse('cart'))

class CheckoutView(CartMixin, NotificationsMixin, views.View):
    """Отображает страницу оформления заказа"""
    def get(self, request, *args, **kwargs):
        initial_data = {}
        if request.user.is_authenticated:
            # Пробуем получить данные из Customer
            try:
                customer = Customer.objects.get(user = request.user)
                initial_data = {
                    'first_name': customer.user.first_name or customer.first_name,
                    'last_name': customer.user.last_name or customer.last_name,
                    'phone': customer.phone,
                    'address': customer.address,
                }
            except Customer.DoesNotExist:
                # Если Customer не существует, используем данные из User
                initial_data = {
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                }

        form = OrderForm(initial = initial_data)
        context = {
            'cart': self.cart,
            'form': form,
            'notifications': self.notifications(request.user),
        }
        return render(request, 'pages/cart.html', context)