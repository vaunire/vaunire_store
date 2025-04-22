from django import views
from django.shortcuts import render
from django.db.models import Max, Min

from cart.mixins import CartMixin
from accounts.mixins import NotificationsMixin
from catalog.models import Album, Genre, Style

from .models import Album, Artist


class BaseView(CartMixin, NotificationsMixin, views.View):
    def get(self, request, *args, **kwargs):
        albums = Album.objects.all()
        genres = Genre.objects.all()
        styles = Style.objects.all()

        # Получаем минимальную и максимальную цену из активного прайс-листа
        price_range = albums.aggregate(
            min_price = Min('items__price'),
            max_price = Max('items__price')
        )
        min_price_default = int(price_range['min_price'] or 0)
        max_price_default = int(price_range['max_price'] or 10000)

        # Фильтры из GET-запроса
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        selected_genres = request.GET.getlist('genres')
        selected_styles = request.GET.getlist('styles')
        in_stock = request.GET.get('in_stock')

        # Применяем фильтры
        if min_price:
            albums = albums.filter(items__price__gte = float(min_price))
        if max_price:
            albums = albums.filter(items__price__lte = float(max_price))
        if selected_genres:
            albums = albums.filter(genre__id__in = selected_genres)
        if selected_styles:
            albums = albums.filter(styles__id__in = selected_styles).distinct() # distinct() убирает дубликаты
        if in_stock:
            albums = albums.filter(stock__gt=0)

        # Сортировка по новизне
        albums = albums.order_by('-id')

        context = {
            'albums': albums,
            'genres': genres,
            'styles': styles,
            'min_price': min_price or min_price_default,
            'max_price': max_price or max_price_default,
            'min_price_default': min_price_default,
            'max_price_default': max_price_default,
            'selected_genres': selected_genres,
            'selected_styles': selected_styles,
            'in_stock': in_stock,
            'cart': self.cart,
            'notifications': self.notifications(request.user),
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
