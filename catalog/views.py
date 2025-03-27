from django import views
from django.shortcuts import render

from cart.mixins import CartMixin
from accounts.mixins import NotificationsMixin

from .models import Album, Artist

class BaseView(CartMixin, NotificationsMixin, views.View):
    """Отображает главную страницу сайта"""
    def get(self, request, *args, **kwargs):
        albums = Album.objects.all().order_by('-id')[:5]
        context = {
            'albums': albums,
            'cart': self.cart,
            'notifications': self.notifications(request.user)
        }
        return render(request, 'base.html', context)

class ArtistDetailView(CartMixin,views.generic.DetailView):
    """Отображает детальную страницу исполнителя по его slug"""
    model = Artist
    template_name = 'artist/artist_detail.html'
    slug_url_kwarg = 'artist_slug'
    context_object_name = 'artist'

class AlbumDetailView(CartMixin,views.generic.DetailView):
    """Отображает детальную страницу альбома по его slug"""
    model = Album
    template_name = 'album/album_detail.html'
    slug_url_kwarg = 'album_slug'
    context_object_name = 'album'