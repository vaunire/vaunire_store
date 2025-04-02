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
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user = request.user)
        last_paid_order = customer.orders.filter(paid=True).last()
        context = {
            'customer': customer,
            'cart': self.cart,
            'notifications': self.notifications(request.user),
            'last_paid_order': last_paid_order
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
    """Добавляет альбом в список желаний пользователя"""
    @staticmethod
    def get(request, *args, **kwargs):
        album = Album.objects.get(id = kwargs['album_id'])
        customer = Customer.objects.get(user = request.user)
        customer.wishlist.add(album)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class RemoveFromWishlist(views.View):
    """Удаляет альбом из списка желаний пользователя"""
    @staticmethod
    def get(request, *args, **kwargs):
        album = Album.objects.get(id = kwargs['album_id'])
        customer = Customer.objects.get(user = request.user)
        customer.wishlist.remove(album)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class ClearNotificationsView(views.View):
    """Помечает все непрочитанные уведомления как прочитанные"""
    @staticmethod
    def get(request, *args, **kwargs):
        Notifications.objects.mark_unread_as_read(request.user.customer)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])