from django import views
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Max, Min
from decimal import Decimal
from django.db.models import Q
from django.utils import timezone

from cart.mixins import CartMixin
from accounts.mixins import NotificationsMixin
from catalog.models import Album, Artist, Genre, Style, ImageGallery, PriceList

def search_view(request):
    query = request.GET.get('q', '').strip()
    albums = []
    artists = []

    if query:
        # Поиск альбомов с предзагрузкой исполнителя и галереи изображений
        albums = Album.objects.filter(
            Q(name__icontains=query) | Q(artist__name__icontains=query)
        ).select_related('artist').prefetch_related('image_gallery')[:5]
        # Поиск исполнителей с предзагрузкой галереи изображений
        artists = Artist.objects.filter(name__icontains=query).prefetch_related('image_gallery')[:5]

    return render(request, 'partials/catalog/search_results.html', {
        'albums': albums,
        'artists': artists,
        'query': query
    })

class BaseView(CartMixin, NotificationsMixin, views.View):
    """Базовый класс для всех представлений каталога"""
    def get(self, request, *args, **kwargs):
        albums = Album.objects.all()
        genres = Genre.objects.all()
        styles = Style.objects.all()

        # Получаем фиксированный диапазон цен на основе всех альбомов
        def get_price_range(album_queryset):
            min_price = Decimal('9999999')
            max_price = Decimal('0')
            for album in album_queryset:
                price = album.discounted_price
                min_price = min(min_price, price)
                max_price = max(max_price, price)
            return {
                'min_price': min_price if min_price != Decimal('9999999') else Decimal('0'),
                'max_price': max_price if max_price != Decimal('0') else Decimal('10000')
            }

        price_range = get_price_range(albums)
        year_range = albums.aggregate(
            min_year=Min('release_date__year'),
            max_year=Max('release_date__year')
        )

        # Устанавливаем фиксированные значения по умолчанию
        min_price_default = int(price_range['min_price'] or 0)
        max_price_default = int(price_range['max_price'] or 10000)
        min_year_default = int(year_range['min_year'] or 1900)
        max_year_default = int(year_range['max_year'] or 2025)

        # Собираем активные фильтры
        active_filters = {}
        albums_query = albums

        # Применяем фильтры
        if 'min_price' in request.GET and request.GET['min_price']:
            try:
                min_price = float(request.GET['min_price'])
                albums_query = albums_query.filter(id__in=[
                    album.id for album in albums if album.discounted_price >= min_price
                ])
                active_filters['min_price'] = min_price
            except ValueError:
                active_filters['min_price'] = None
        else:
            active_filters['min_price'] = None

        if 'max_price' in request.GET and request.GET['max_price']:
            try:
                max_price = float(request.GET['max_price'])
                albums_query = albums_query.filter(id__in=[
                    album.id for album in albums if album.discounted_price <= max_price
                ])
                active_filters['max_price'] = max_price
            except ValueError:
                active_filters['max_price'] = None
        else:
            active_filters['max_price'] = None

        if 'min_year' in request.GET and request.GET['min_year']:
            try:
                min_year = int(request.GET['min_year'])
                albums_query = albums_query.filter(release_date__year__gte=min_year)
                active_filters['min_year'] = min_year
            except ValueError:
                active_filters['min_year'] = None
        else:
            active_filters['min_year'] = None

        if 'max_year' in request.GET and request.GET['max_year']:
            try:
                max_year = int(request.GET['max_year'])
                albums_query = albums_query.filter(release_date__year__lte=max_year)
                active_filters['max_year'] = max_year
            except ValueError:
                active_filters['max_year'] = None
        else:
            active_filters['max_year'] = None

        if 'genres' in request.GET and request.GET.getlist('genres'):
            selected_genres = request.GET.getlist('genres')
            albums_query = albums_query.filter(genre__id__in=selected_genres)
            active_filters['selected_genres'] = selected_genres
        else:
            active_filters['selected_genres'] = []

        if 'styles' in request.GET and request.GET.getlist('styles'):
            selected_styles = request.GET.getlist('styles')
            albums_query = albums_query.filter(styles__id__in=selected_styles).distinct()
            active_filters['selected_styles'] = selected_styles
        else:
            active_filters['selected_styles'] = []

        if 'conditions' in request.GET and request.GET.getlist('conditions'):
            selected_conditions = request.GET.getlist('conditions')
            albums_query = albums_query.filter(condition__in=selected_conditions)
            active_filters['selected_conditions'] = selected_conditions
        else:
            active_filters['selected_conditions'] = []

        if 'format_editions' in request.GET and request.GET.getlist('format_editions'):
            selected_format_editions = request.GET.getlist('format_editions')
            albums_query = albums_query.filter(format_edition__in=selected_format_editions)
            active_filters['selected_format_editions'] = selected_format_editions
        else:
            active_filters['selected_format_editions'] = []

        if 'in_stock' in request.GET and request.GET['in_stock'] == '1':
            albums_query = albums_query.filter(stock__gt=0)
            active_filters['in_stock'] = True
        else:
            active_filters['in_stock'] = False

        if 'offer_of_the_week' in request.GET and request.GET['offer_of_the_week'] == '1':
            albums_query = albums_query.filter(offer_of_the_week=True)
            active_filters['offer_of_the_week'] = True
        else:
            active_filters['offer_of_the_week'] = False

        # Устанавливаем текущие значения фильтров для ползунков
        min_price = active_filters['min_price'] if active_filters['min_price'] is not None else min_price_default
        max_price = active_filters['max_price'] if active_filters['max_price'] is not None else max_price_default
        min_year = active_filters['min_year'] if active_filters['min_year'] is not None else min_year_default
        max_year = active_filters['max_year'] if active_filters['max_year'] is not None else max_year_default

        # Получаем уникальные значения для фильтров
        conditions = albums_query.values_list('condition', flat=True).distinct().exclude(condition__isnull=True).exclude(condition='')
        format_editions = albums_query.values_list('format_edition', flat=True).distinct().exclude(format_edition__isnull=True).exclude(format_edition='')

        # Сортировка по новизне
        albums_query = albums_query.order_by('-id')

        # Получаем самый продаваемый альбом месяца
        month_bestseller = Album.objects.get_month_bestseller()

        # Получаем изображения для слайдера и предложение недели
        image_gallery = ImageGallery.objects.filter(use_in_slider=True)
        offer_of_the_week = Album.objects.filter(offer_of_the_week=True).first()

        # Пагинация
        paginator = Paginator(albums_query, 12)  # 12 альбомов на страницу
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'albums': page_obj,
            'genres': genres,
            'styles': styles,
            'conditions': conditions,
            'format_editions': format_editions,
            'min_price': min_price,
            'max_price': max_price,
            'min_year': min_year,
            'max_year': max_year,
            'min_price_default': min_price_default,
            'max_price_default': max_price_default,
            'min_year_default': min_year_default,
            'max_year_default': max_year_default,
            'selected_genres': active_filters['selected_genres'],
            'selected_styles': active_filters['selected_styles'],
            'selected_conditions': active_filters['selected_conditions'],
            'selected_format_editions': active_filters['selected_format_editions'],
            'in_stock': active_filters['in_stock'],
            'offer_of_the_week': active_filters['offer_of_the_week'],
            'active_filters': active_filters,
            'cart': self.cart,
            'notifications': self.notifications(request.user),
            'page_obj': page_obj,
            'month_bestseller': month_bestseller,
            'image_gallery': image_gallery,
            'offer_of_the_week_album': offer_of_the_week
        }

        return render(request, 'base.html', context)

class ArtistDetailView(CartMixin, views.generic.DetailView, NotificationsMixin):
    """Отображает детальную страницу исполнителя по его slug"""
    model = Artist
    template_name = 'artist/artist_detail.html'
    slug_url_kwarg = 'artist_slug'
    context_object_name = 'artist'

class AlbumDetailView(CartMixin, views.generic.DetailView, NotificationsMixin):
    """Отображает детальную страницу альбома по его slug"""
    model = Album
    template_name = 'album/album_detail.html'
    slug_url_kwarg = 'album_slug'
    context_object_name = 'album'