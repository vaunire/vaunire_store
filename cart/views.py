from django import views
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render

from catalog.models import Album
from accounts.mixins import NotificationsMixin

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
        cart_product, created = CartProduct.objects.get_or_create(
            user = self.cart.owner,
            cart = self.cart,
            content_type = content_type,
            object_id = product.id
        )
        if created:
            self.cart.products.add(cart_product)
        self.cart.update_totals()
        messages.add_message(request, messages.INFO, "Товар успешно добавлен")
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class RemoveFromCartView(CartMixin, views.View):
    """Удаляет товар из корзины и обновляет её итоги"""
    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'),kwargs.get('slug')
        content_type = ContentType.objects.get(model = ct_model)
        product = content_type.model_class().objects.get(slug = product_slug)
        cart_product = CartProduct.objects.get(
            user = self.cart.owner,
            cart = self.cart,
            content_type = content_type,
            object_id = product.id
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        self.cart.update_totals()
        messages.add_message(request, messages.INFO, f"Товар '{product.name}' успешно удалён из корзины.")
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class ChangeQuantityView(CartMixin, views.View):
    """Обновляет количество товара в корзине и пересчитывает итоги"""
    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model = ct_model)
        product = content_type.model_class().objects.get(slug = product_slug)
        cart_product = CartProduct.objects.get(
            user = self.cart.owner,
            cart = self.cart,
            content_type = content_type,
            object_id = product.id
        )
        quantity = int(request.POST.get('quantity'))
        cart_product.quantity = quantity
        cart_product.save() 
        self.cart.update_totals()
        messages.add_message(request, messages.INFO, f"Количество товара '{product.name}' успешно изменено на {quantity}.")
        return HttpResponseRedirect(request.META['HTTP_REFERER'])