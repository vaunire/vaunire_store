from django import views
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from accounts.mixins import NotificationsMixin
from accounts.models import Customer
from cart.mixins import CartMixin
from cart.models import Cart
from catalog.models import Artist

from .forms import OrderForm
from .models import Order


class CheckoutView(CartMixin, NotificationsMixin, views.View):
    """Отображает страницу оформления заказа"""
    def get(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'form': form,
            'notifications': self.notifications(request.user)
        }
        return render(request, 'pages/cart.html', context)

class MakeOrderView(CartMixin, views.View):
    """Создаёт новый заказ на основе данных из формы, проверяет наличие товаров и их количество на складе, сохраняет заказ и обновляет остатки"""
    # Атомарность: свойство, которое гарантирует, что транзакция либо будет полностью завершена, либо не будет выполнена вообще.
    @transaction.atomic 
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user = request.user)
        if form.is_valid():
            # Списки для хранения проблемных товаров
            out_of_stock = []
            more_than_on_stock = []

            out_of_stock_messages = ""
            more_than_on_stock_messages = ""
            # Проверка доступности товаров в корзине
            for item in self.cart.products.all():
                # Если товара нет в наличии
                if not item.content_object.stock:
                    out_of_stock.append(' - '.join([
                        item.content_object.artist.name, item.content_object.name
                    ]))
                # Если заказанное количество превышает наличие
                if item.content_object.stock and item.content_object.stock < item.quantity: 
                    more_than_on_stock.append(
                        {
                        'product': ' - '.join([item.content_object.artist.name, item.content_object.name]),
                        'stock': item.content_object.stock, 'quantity': item.quantity
                        }
                    )
            if out_of_stock:
                out_of_stock_products = ', '.join(out_of_stock)
                out_of_stock_messages = f"Следующих товаров нет в наличии: {out_of_stock_products}. " \
                                         "Пожалуйста, удалите их из корзины или дождитесь пополнения запасов.\n" 
            if more_than_on_stock:
                for item in more_than_on_stock:
                    more_than_on_stock_messages += f"Товар '{item['product']}': в наличии {item['stock']} шт., заказано {item['quantity']} шт." \
                                                    "Пожалуйста, скорректируйте количество.\n"
            # Формирование сообщений об ошибках
            error_message_for_customer = ""
            if out_of_stock:
                error_message_for_customer = out_of_stock_messages + '\n'
            if more_than_on_stock:
                error_message_for_customer += more_than_on_stock_messages + '\n'
            if error_message_for_customer:
                messages.add_message(request, messages.INFO, error_message_for_customer)
                return redirect('checkout')
            
            # Создание нового заказа
            new_order = form.save(commit = False) # commit = False: Создаем заказ, но не сохраняем сразу в БД
            new_order.customer = customer
            new_order.cart = self.cart
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()

            # Обновляем корзину и связываем с заказом
            self.cart.in_order = True
            self.cart.save()
            new_order.save()
            customer.orders.add(new_order)

            # Обновление остатков на складе
            for item in self.cart.products.all():
                item.content_object.stock -= item.quantity
                item.content_object.save()

            messages.success(request, 'Спасибо за заказ! Менеджер свяжется с вами в ближайшее время.')
            return redirect('/')
        # Если форма невалидна, возвращаем пользователя на страницу оформления
        return redirect('cart')
