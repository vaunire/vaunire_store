from django import views

# Миксины — классы для добавления общей функциональности в представления.
# Они помогают избежать дублирования кода и делают его более модульным.

from .models import Cart
from accounts.models import Customer

class CartMixin(views.generic.detail.SingleObjectMixin, views.View):
    def dispatch(self, request, *args, **kwargs):
        """
        Обрабатывает запрос перед вызовом методов get/post, создаёт или получает корзину пользователя
        Устанавливает self.cart для использования в представлении
        """
        cart = None
        if request.user.is_authenticated:
            # Получаем или создаём профиль покупателя
            customer, created = Customer.objects.get_or_create(
                user = request.user,
                defaults = {'phone': '', 'email': request.user.email or '', 'first_name': request.user.first_name, 'last_name': request.user.last_name}
            )
            # Ищем активную корзину (не в заказе) или создаём новую
            cart = Cart.objects.filter(owner = customer, in_order = False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        self.cart = cart  # Сохраняем корзину в атрибут экземпляра
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Добавляет объект корзины в контекст шаблона для использования в рендеринге"""
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context