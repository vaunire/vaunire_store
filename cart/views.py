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
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)

        # Проверяем, есть ли уже такой продукт в корзине
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner,
            cart=self.cart,
            content_type=content_type,
            object_id=product.id,
            defaults={'quantity': 1}
        )

        if not created:
            cart_product.quantity += 1
            cart_product.save()
        else:
            self.cart.products.add(cart_product)

        self.cart.update_totals()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class RemoveFromCartView(CartMixin, views.View):
    """Удаляет товар из корзины и обновляет её итоги"""
    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)

        cart_product = CartProduct.objects.filter(
            user=self.cart.owner,
            cart=self.cart,
            content_type=content_type,
            object_id=product.id
        ).first()

        cart_product.delete()
        self.cart.update_totals()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class ChangeQuantityView(CartMixin, views.View):
    """Обновляет количество товара в корзине и пересчитывает итоги"""
    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)

        cart_product = CartProduct.objects.filter(
            user=self.cart.owner,
            cart=self.cart,
            content_type=content_type,
            object_id=product.id
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
        self.cart.update_totals()
        self.cart.save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])