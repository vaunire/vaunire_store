from datetime import timedelta

import stripe
from django import views
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from accounts.models import Customer
from cart.mixins import CartMixin
from cart.models import Cart, CartProduct
from catalog.models import Artist

from .forms import OrderForm
from .models import Order, Payment, ReturnRequest

# Настройка Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

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

            # Обновление данных в Customer
            customer.first_name = form.cleaned_data['first_name']
            customer.last_name = form.cleaned_data['last_name']
            customer.phone = form.cleaned_data['phone']
            customer.address = form.cleaned_data['address']
            customer.save()

            # Обновление остатков на складе
            for item in self.cart.products.all():
                item.content_object.stock -= item.quantity
                item.content_object.save()
            
            # Создание сессии Stripe
            try:
                # Конвертируем final_price в копейки (Почему-то Stripe понимает сумму только в мин. единицах валюты)
                amount = int(self.cart.final_price * 100)
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types = ['card'],
                    line_items = [
                        {
                            'price_data': {
                                'currency': 'rub',
                                'product_data': {
                                    'name': f'Заказ №{new_order.id}',
                                },
                                'unit_amount': amount,
                            },
                            'quantity': 1,
                        },
                    ],
                    mode = 'payment',
                    success_url = request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url = request.build_absolute_uri(reverse('payment_cancel')),
                    metadata = {'order_id': new_order.id},
                )

                # Создаем запись о платеже
                Payment.objects.create(
                    order = new_order,
                    amount = self.cart.final_price,
                    payment_id = checkout_session.id,
                    status = 'pending',
                    payment_method = 'Stripe'
                )

                # Помечаем корзину как in_order только после создания платежа
                self.cart.in_order = True
                self.cart.save()
                customer.orders.add(new_order)

                # Перенаправляем на страницу оплаты Stripe
                return redirect(checkout_session.url, code = 303)

            except stripe.error.StripeError as e:
                messages.error(request, 'Ошибка при создании платежа. Пожалуйста, попробуйте снова.')
                return redirect('checkout')

        else:
            messages.error(request, 'Мы уже держим ваш заказ, осталось лишь немного поправить!')
        print("Form errors:", form.errors)  
        # Если форма невалидна, возвращаем пользователя на страницу оформления
        return redirect('cart')
    
class PaymentSuccessView(views.View):
    """Обрабатывает успешную оплату"""
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        if not session_id:
            return redirect('/')
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            order_id = session.metadata.get('order_id')
            order = Order.objects.get(id=order_id)

            # Проверяем, не был ли заказ уже оплачен
            if not order.paid:
                order.paid = True
                order.status = 'in_progress'  # Обновляем статус заказа
                order.save()

                payment = Payment.objects.get(payment_id=session_id)
                payment.status = 'success'
                payment.payment_date = timezone.now()
                payment.save()

                messages.success(request, 'Оплата прошла успешно! Ваш заказ в обработке.')
            else:
                messages.info(request, 'Заказ уже был оплачен.')
            return redirect('/')

        except (stripe.error.StripeError, Order.DoesNotExist, Payment.DoesNotExist):
            messages.error(request, 'Ошибка при обработке платежа.')
            return redirect('/')

class PaymentCancelView(views.View):
    """Обрабатывает отмену оплаты"""
    def get(self, request, *args, **kwargs):
        messages.error(request, 'Оплата была отменена. Вы можете попробовать снова.')
        return redirect('cart')

class StripeWebhookView(views.View):
    """
    Класс для обработки вебхуков Stripe.

    Цель:
    - Принимать уведомления от Stripe о событиях (например, успешная оплата).
    - Обновлять заказы и платежи в базе данных для надёжного учёта транзакций.

    Вебхуки — это POST-запросы от Stripe, отправляемые на сервер при событиях.
    Этот класс проверяет подлинность запросов и обрабатывает событие checkout.session.completed.

    Полезное видео для понимания вебхуков:
    - Listen IT | Что такое Webhook за 12 минут - https://www.youtube.com/watch?v=_NlHzAaLH4g&t=86s

    Возвращает:
            HttpResponse: Статус 200 (успех) или 400 (ошибка).
    """
    @method_decorator(csrf_exempt) 
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Извлечение данных запроса
        payload = request.body # Тело запроса с JSON-данными события
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')  # Подпись для проверки
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        try:
            # Валидация подписи для защиты от поддельных запросов
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            # Возвращаем ошибку 400, если тело запроса некорректно
            return HttpResponse(status = 400)
        except stripe.error.SignatureVerificationError:
            # Возвращаем ошибку 400, если подпись не совпадает, что указывает на поддельный запрос
            return HttpResponse(status = 400)

        # Обрабатываем событие успешной оплаты (checkout.session.completed)
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            order_id = session.get('metadata', {}).get('order_id')

            # Если метаданные отсутствуют или order_id неверный, обработка пропускается
            if not order_id:
                return HttpResponse(status = 200)  # Возвращаем 200, чтобы не блокировать Stripe

            # Обновляем заказ и платёж в базе данных
            try:
                order = Order.objects.get(id = order_id)
                if not order.paid:
                    order.paid = True
                    order.status = 'in_progress'
                    order.save()

                    # Находим связанный платёж по ID сессии Stripe
                    payment = Payment.objects.get(payment_id = session['id'])
                    payment.status = 'success'
                    payment.payment_date = timezone.now()
                    payment.save()
            except (Order.DoesNotExist, Payment.DoesNotExist):
                # Заказ или платёж не найдены (например, удалены или неверный ID)
                pass
        # Возвращаем HTTP-ответ 200, чтобы уведомить Stripe об успешной обработке
        return HttpResponse(status = 200)

class SubmitReturnView(views.View):
    """Обрабатывает запрос на возврат товара"""
    def post(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id = order_id, customer__user = request.user)
            customer = order.customer
        except Order.DoesNotExist:
            messages.error(request, 'Заказ не найден или вы не имеете к нему доступа.')
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        # Проверка срока подачи возврата (14 дней с даты получения)
        if order.order_date < timezone.now() - timedelta(days = 14):
            messages.error(request, 'Срок для подачи запроса на возврат истек.')
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        # Получение данных из формы
        product_ids = request.POST.getlist('return-products')
        reason = request.POST.get('return-reason')
        details = request.POST.get('return-details', '')
        file = request.FILES.get('return-file')

        # Проверка, что товары принадлежат заказу
        products = CartProduct.objects.filter(id__in = product_ids, cart = order.cart)
        if not products.exists():
            messages.error(request, 'Выбранные товары не относятся к этому заказу.')
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        # Создание запроса на возврат
        return_request = ReturnRequest.objects.create(
            customer = customer,
            order = order,
            reason = reason,
            details = details,
            file = file if file else None
        )
        return_request.products.set(products)

        messages.success(request, 'Запрос на возврат успешно отправлен. Мы свяжемся с вами в ближайшее время.')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class CancelReturnView(views.View):
    """Отменяет/Удаляет заявку на возврат"""
    def get(self, request, return_id, *args, **kwargs):
        try:
            return_request = ReturnRequest.objects.get(
                id = return_id,
                order__customer__user = request.user,
                status = 'pending'
            )
            return_request.delete() 
            messages.success(request, 'Заявка на возврат успешно отменена.')
        except ReturnRequest.DoesNotExist:
            messages.error(request, 'Заявка не найдена или не может быть отменена.')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])