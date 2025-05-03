from django import views
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from catalog.models import Album
from cart.mixins import CartMixin

from orders.models import Order

from .mixins import NotificationsMixin
from .models import Customer, Notifications  
from .forms import LoginForm, RegistrationForm, ProfileEditForm

class AccountView(CartMixin, NotificationsMixin, views.View):
    def get(self, request, tab='account', *args, **kwargs):
        try:
            customer = request.user.customer
        except (Customer.DoesNotExist, AttributeError):
            customer = None

        orders = customer.orders.order_by('-created_at') if customer else []
        last_paid_order = None
        if customer:
            last_paid_order = customer.orders.filter(paid=True).last()

        valid_tabs = ['account', 'orders', 'wishlist', 'returns']
        if tab not in valid_tabs:
            tab = 'account'

        orders_with_status = []
        for order in orders:
            has_pending_return = order.return_requests.filter(status = 'pending').exists()
            has_approved_return = order.return_requests.filter(status = 'approved').exists()
            has_canceled_return = order.return_requests.filter(status = 'canceled').exists()
            has_paid_return = order.return_requests.filter(status = 'paid').exists()
            orders_with_status.append({
                'order': order,
                'has_pending_return': has_pending_return,
                'has_approved_return': has_approved_return,
                'has_canceled_return': has_canceled_return,
                'has_paid_return': has_paid_return
            })

        highlighted_order_id = request.GET.get('order_id')

        # Создаём форму для начального состояния
        form = ProfileEditForm(instance = request.user, customer = customer)

        context = {
            'customer': customer,
            'cart': self.cart,
            'notifications': self.notifications(request.user),
            'orders_with_status': orders_with_status,
            'last_paid_order': last_paid_order,
            'active_tab': tab,
            'highlighted_order_id': highlighted_order_id,
            'form': form,
            'is_editing': False,
        }
        return render(request, 'pages/account.html', context)

class LoginView(views.View):
    """Проверяет введённые данные, аутентифицирует пользователя и выполняет вход"""
    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'auth/login.html', context)
    
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username = username, password = password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'auth/login.html', context)
    
class RegistrationView(views.View):
    """Проверяет введённые данные, создаёт пользователя и выполняет вход"""
    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'auth/registration.html', context)
    
    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit = False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user = new_user,
                phone = form.cleaned_data['phone']
            )
            user = authenticate(username = form.cleaned_data['username'], password = form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'auth/registration.html', context)
    
@method_decorator(login_required, name = 'dispatch') # Декоратор проверки авторизации 
class UpdateProfileView(CartMixin, NotificationsMixin, views.View):
    def get(self, request, *args, **kwargs):
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            customer = Customer(user=request.user)
            customer.save()

        is_editing = request.GET.get('edit', False)
        form = ProfileEditForm(instance = request.user, customer = customer)

        return render(request, 'pages/account.html', {
            'form': form,
            'customer': customer,
            'is_editing': is_editing,
            'active_tab': 'account',
            'cart': self.cart,
            'notifications': self.notifications(request.user),
        })

    def post(self, request, *args, **kwargs):
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            customer = Customer(user=request.user)
            customer.save()

        form = ProfileEditForm(request.POST, instance=request.user, customer=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('account_tab', tab='account')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

        return render(request, 'pages/account.html', {
            'form': form,
            'customer': customer,
            'is_editing': True,
            'active_tab': 'account',
            'cart': self.cart,
            'notifications': self.notifications(request.user),
        })

class FavoritesView(CartMixin, NotificationsMixin, views.View):
    """Представление для отображения избранных альбомов пользователя"""
    def get(self, request, *args, **kwargs):
        # Получаем клиента, связанного с пользователем
        customer = request.user.customer
        # Получаем все альбомы из списка избранного
        albums = customer.favorite.all().order_by('-id').distinct()

        # Пагинация: 15 альбомов на страницу (5 в строке, 3 строки)
        paginator = Paginator(albums, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'albums': page_obj, 
            'page_obj': page_obj,
            'cart': self.cart,
            'notifications': self.notifications(request.user),
        }
        return render(request, 'pages/favorites.html', context)

class AddToWishlist(views.View):
    """Добавляет альбом в список ожидания пользователя"""
    @staticmethod
    def get(request, *args, **kwargs):
        album = Album.objects.get(id = kwargs['album_id'])
        customer = Customer.objects.get(user = request.user)
        customer.wishlist.add(album)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class RemoveFromWishlist(views.View):
    """Удаляет альбом из списка ожидания пользователя"""
    @staticmethod
    def get(request, *args, **kwargs):
        album = Album.objects.get(id = kwargs['album_id'])
        customer = Customer.objects.get(user = request.user)
        customer.wishlist.remove(album)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class AddToFavorite(views.View):
    """Добавляет альбом в избранное пользователя"""
    @staticmethod
    def get(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login/')
        album = Album.objects.get(id=kwargs['album_id'])
        customer = Customer.objects.get(user=request.user)
        customer.favorite.add(album)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class RemoveFromFavorite(views.View):
    """Удаляет альбом из избранного пользователя"""
    @staticmethod
    def get(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login/')
        album = Album.objects.get(id=kwargs['album_id'])
        customer = Customer.objects.get(user=request.user)
        customer.favorite.remove(album)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class ClearNotificationsView(views.View):
    """Помечает все непрочитанные уведомления как прочитанные"""
    @staticmethod
    def get(request, *args, **kwargs):
        Notifications.objects.mark_unread_as_read(request.user.customer)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

def dashboard_callback(request, context):
    # Получаем данные за последние 14 дней
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=14)

    # Данные для графика регистраций
    registrations = Customer.objects.filter(
        last_updated__date__range=[start_date, end_date]
    ).extra(
        select={'day': 'date(last_updated)'}
    ).values('day').annotate(count=models.Count('id')).order_by('day')

    registration_labels = []
    registration_counts = []
    current_date = start_date
    while current_date <= end_date:
        registration_labels.append(current_date.strftime('%Y-%m-%d'))
        count = next((item['count'] for item in registrations if item['day'] == current_date), 0)
        registration_counts.append(count)
        current_date += timedelta(days=1)

    # Данные для графика заказов
    orders = Order.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(count=models.Count('id')).order_by('day')

    order_labels = []
    order_counts = []
    current_date = start_date
    while current_date <= end_date:
        order_labels.append(current_date.strftime('%Y-%m-%d'))
        count = next((item['count'] for item in orders if item['day'] == current_date), 0)
        order_counts.append(count)
        current_date += timedelta(days=1)

    # Данные для таблицы последних альбомов
    latest_albums = Album.objects.select_related('artist').order_by('-id')[:5]

    context.update({
        "registration_data": {
            "labels": registration_labels,
            "counts": registration_counts
        },
        "order_data": {
            "labels": order_labels,
            "counts": order_counts
        },
        "latest_albums": latest_albums
    })

    return context