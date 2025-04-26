from django import views
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Max, Min

from cart.mixins import CartMixin
from accounts.mixins import NotificationsMixin
from catalog.models import Album, Artist, Genre, Style

class BaseView(CartMixin, NotificationsMixin, views.View):
    """Базовый класс для всех представлений каталога"""
    def get(self, request, *args, **kwargs):
        albums = Album.objects.all()
        genres = Genre.objects.all()
        styles = Style.objects.all()

        # Получаем минимальную и максимальную цену из активного прайс-листа
        price_range = albums.aggregate(
            min_price=Min('items__price'),
            max_price=Max('items__price')
        )
        min_price_default = int(price_range['min_price'] or 0)
        max_price_default = int(price_range['max_price'] or 10000)

        # Получаем минимальный и максимальный год выпуска
        year_range = albums.aggregate(
            min_year=Min('release_date__year'),
            max_year=Max('release_date__year')
        )
        min_year_default = int(year_range['min_year'] or 1900)
        max_year_default = int(year_range['max_year'] or 2025)

        # Получаем уникальные значения для фильтров
        conditions = Album.objects.values_list('condition', flat=True).distinct().exclude(condition__isnull=True).exclude(condition='')
        format_editions = Album.objects.values_list('format_edition', flat=True).distinct().exclude(format_edition__isnull=True).exclude(format_edition='')

        # Фильтры из GET-запроса
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        min_year = request.GET.get('min_year')
        max_year = request.GET.get('max_year')
        selected_genres = request.GET.getlist('genres')
        selected_styles = request.GET.getlist('styles')
        selected_conditions = request.GET.getlist('conditions')
        selected_format_editions = request.GET.getlist('format_editions')
        in_stock = request.GET.get('in_stock')
        offer_of_the_week = request.GET.get('offer_of_the_week')

        # Применяем фильтры
        if min_price:
            albums = albums.filter(items__price__gte=float(min_price))
        if max_price:
            albums = albums.filter(items__price__lte=float(max_price))
        if min_year:
            albums = albums.filter(release_date__year__gte=int(min_year))
        if max_year:
            albums = albums.filter(release_date__year__lte=int(max_year))
        if selected_genres:
            albums = albums.filter(genre__id__in=selected_genres)
        if selected_styles:
            albums = albums.filter(styles__id__in=selected_styles).distinct()
        if selected_conditions:
            albums = albums.filter(condition__in=selected_conditions)
        if selected_format_editions:
            albums = albums.filter(format_edition__in=selected_format_editions)
        if in_stock:
            albums = albums.filter(stock__gt=0)
        if offer_of_the_week:
            albums = albums.filter(offer_of_the_week=True)

        # Сортировка по новизне
        albums = albums.order_by('-id')

        # Пагинация
        paginator = Paginator(albums, 12)  # 12 альбомов на страницу
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'albums': page_obj, 
            'genres': genres,
            'styles': styles,
            'conditions': conditions,
            'format_editions': format_editions,
            'min_price': min_price or min_price_default,
            'max_price': max_price or max_price_default,
            'min_price_default': min_price_default,
            'max_price_default': max_price_default,
            'min_year': min_year or min_year_default,
            'max_year': max_year or max_year_default,
            'min_year_default': min_year_default,
            'max_year_default': max_year_default,
            'selected_genres': selected_genres,
            'selected_styles': selected_styles,
            'selected_conditions': selected_conditions,
            'selected_format_editions': selected_format_editions,
            'in_stock': in_stock,
            'offer_of_the_week': offer_of_the_week,
            'cart': self.cart,
            'notifications': self.notifications(request.user),
            'page_obj': page_obj
        }
        return render(request, 'base.html', context)

class ArtistDetailView(CartMixin,views.generic.DetailView, NotificationsMixin):
    """Отображает детальную страницу исполнителя по его slug"""
    model = Artist
    template_name = 'artist/artist_detail.html'
    slug_url_kwarg = 'artist_slug'
    context_object_name = 'artist'

class AlbumDetailView(CartMixin,views.generic.DetailView, NotificationsMixin):
    """Отображает детальную страницу альбома по его slug"""
    model = Album
    template_name = 'album/album_detail.html'
    slug_url_kwarg = 'album_slug'
    context_object_name = 'album'
