from django import views
from django.http import HttpResponseRedirect
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse

from cart.models import Cart
from accounts.models import Customer

class CartMixin(views.generic.detail.SingleObjectMixin, views.View):
    def dispatch(self, request, *args, **kwargs):
        """
        Обрабатывает запрос перед вызовом методов get/post, создаёт или получает корзину пользователя.
        Устанавливает self.cart для использования в представлении.
        Для анонимных пользователей корзина не создаётся (self.cart = None).
        """
        cart = None
        if request.user.is_authenticated:
            # Получаем или создаём профиль покупателя
            customer, created = Customer.objects.get_or_create(
                user=request.user,
                defaults={
                    'phone': '',
                    'email': request.user.email or '',
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name
                }
            )
            # Ищем активную корзину (не в заказе)
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                try:
                    cart = Cart.objects.create(owner=customer)
                except Exception as e:
                    print(f"Ошибка при создании корзины: {e}")
                    # Попробуем получить последнюю корзину
                    cart = Cart.objects.filter(owner=customer).last()
                    if not cart:
                        raise Exception("Не удалось обработать корзину. Пожалуйста, попробуйте позже.")
        # Для анонимных пользователей корзина не создаётся
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Добавляет объект корзины в контекст шаблона для использования в рендеринге"""
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context