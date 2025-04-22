from django import views
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.http import HttpResponseRedirect

from catalog.models import Album
from cart.mixins import CartMixin

from .mixins import NotificationsMixin
from .models import Customer, Notifications  
from .forms import LoginForm, RegistrationForm  

class AccountView(CartMixin, NotificationsMixin, views.View):
    """Отображает страницу личного кабинета пользователя"""
    def get(self, request, tab = 'account', *args, **kwargs):
        customer = None
        last_paid_order = None
        try:
            customer = Customer.objects.get(user = request.user)
            last_paid_order = customer.orders.filter(paid = True).last()
        except (Customer.DoesNotExist, AttributeError):
            pass

        valid_tabs = ['account', 'orders', 'wishlist', 'returns']
        if tab not in valid_tabs:
            tab = 'account'

        context = {
            'customer': customer,
            'cart': self.cart,
            'notifications': self.notifications(request.user),
            'last_paid_order': last_paid_order,
            'active_tab': tab
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
                messages.success(request, 'Добро пожаловать в мир музыки!')
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
            messages.success(request, 'Вы успешно зарегистрировались!')
            return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'auth/registration.html', context)

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