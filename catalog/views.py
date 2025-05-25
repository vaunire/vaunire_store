from django import views
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Min, Max, OuterRef, Subquery, F, Case, When, Value, DecimalField
from django.utils import timezone
from decimal import Decimal
from django.db.models import Q

from cart.mixins import CartMixin
from accounts.mixins import NotificationsMixin
from catalog.models import Album, Artist, Genre, Style, ImageGallery, PriceList, PriceListItem
from promotions.models import Promotion

def search_view(request):
    query = request.GET.get('q', '').strip()
    albums = []
    artists = []

    if query:
        albums = Album.objects.filter(
            Q(name__icontains=query) | Q(artist__name__icontains=query)
        ).select_related('artist').prefetch_related('image_gallery')[:5]
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

        # Получаем диапазон цен с учетом скидок
        def get_price_range(album_queryset):
            active_pricelist = PriceList.objects.filter(is_active=True).first()
            if not active_pricelist:
                return {'min_price': Decimal('0'), 'max_price': Decimal('10000')}

            price_subquery = PriceListItem.objects.filter(
                album_id=OuterRef('pk'),
                price_list=active_pricelist
            ).values('price')[:1]

            discount_subquery = Promotion.objects.filter(
                albums=OuterRef('pk'),
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ).values('discount_percentage')[:1]

            albums_with_price = album_queryset.annotate(
                annotated_current_price=Subquery(price_subquery, output_field=DecimalField()),
                annotated_discount_percentage=Subquery(discount_subquery, output_field=DecimalField()),
                annotated_discounted_price=Case(
                    When(annotated_discount_percentage__isnull=False,
                         then=F('annotated_current_price') * (1 - F('annotated_discount_percentage') / 100.0)),
                    default=F('annotated_current_price'),
                    output_field=DecimalField()
                )
            )

            price_range = albums_with_price.aggregate(
                min_price=Min('annotated_discounted_price', default=Decimal('0')),
                max_price=Max('annotated_discounted_price', default=Decimal('10000'))
            )
            return {
                'min_price': price_range['min_price'] or Decimal('0'),
                'max_price': price_range['max_price'] or Decimal('10000')
            }

        price_range = get_price_range(albums)
        year_range = albums.aggregate(
            min_year=Min('release_date__year'),
            max_year=Max('release_date__year')
        )

        min_price_default = int(price_range['min_price'] or 0)
        max_price_default = int(price_range['max_price'] or 10000)
        min_year_default = int(year_range['min_year'] or 1900)
        max_year_default = int(year_range['max_year'] or 2025)

        active_filters = {}
        albums_query = albums

        # Получаем активный прайс-лист
        active_pricelist = PriceList.objects.filter(is_active=True).first()

        # Фильтрация по типу носителя
        selected_media_type = request.GET.get('media_type', 'all')
        if selected_media_type != 'all':
            try:
                media_type_id = int(selected_media_type)
                albums_query = albums_query.filter(media_type__id=media_type_id)
                active_filters['selected_media_type'] = selected_media_type
            except (ValueError, MediaType.DoesNotExist):
                active_filters['selected_media_type'] = 'all'
        else:
            active_filters['selected_media_type'] = 'all'

        # Фильтрация по min_price
        if 'min_price' in request.GET and request.GET['min_price']:
            try:
                min_price_str = request.GET['min_price'].replace(',', '.')
                min_price = Decimal(min_price_str)
                if active_pricelist:
                    price_subquery = PriceListItem.objects.filter(
                        album_id=OuterRef('pk'),
                        price_list=active_pricelist
                    ).values('price')[:1]
                    discount_subquery = Promotion.objects.filter(
                        albums=OuterRef('pk'),
                        is_active=True,
                        start_date__lte=timezone.now(),
                        end_date__gte=timezone.now()
                    ).values('discount_percentage')[:1]
                    albums_query = albums_query.annotate(
                        annotated_current_price=Subquery(price_subquery, output_field=DecimalField()),
                        annotated_discount_percentage=Subquery(discount_subquery, output_field=DecimalField()),
                        annotated_discounted_price=Case(
                            When(annotated_discount_percentage__isnull=False,
                                 then=F('annotated_current_price') * (1 - F('annotated_discount_percentage') / 100.0)),
                            default=F('annotated_current_price'),
                            output_field=DecimalField()
                        )
                    ).filter(annotated_discounted_price__gte=min_price)
                active_filters['min_price'] = float(min_price)
            except (ValueError, DecimalException):
                active_filters['min_price'] = None

        # Фильтрация по max_price
        if 'max_price' in request.GET and request.GET['max_price']:
            try:
                max_price_str = request.GET['max_price'].replace(',', '.')
                max_price = Decimal(max_price_str)
                if active_pricelist:
                    price_subquery = PriceListItem.objects.filter(
                        album_id=OuterRef('pk'),
                        price_list=active_pricelist
                    ).values('price')[:1]
                    discount_subquery = Promotion.objects.filter(
                        albums=OuterRef('pk'),
                        is_active=True,
                        start_date__lte=timezone.now(),
                        end_date__gte=timezone.now()
                    ).values('discount_percentage')[:1]
                    albums_query = albums_query.annotate(
                        annotated_current_price=Subquery(price_subquery, output_field=DecimalField()),
                        annotated_discount_percentage=Subquery(discount_subquery, output_field=DecimalField()),
                        annotated_discounted_price=Case(
                            When(annotated_discount_percentage__isnull=False,
                                 then=F('annotated_current_price') * (1 - F('annotated_discount_percentage') / 100.0)),
                            default=F('annotated_current_price'),
                            output_field=DecimalField()
                        )
                    ).filter(annotated_discounted_price__lte=max_price)
                active_filters['max_price'] = float(max_price)
            except (ValueError, DecimalException):
                active_filters['max_price'] = None

        # Фильтрация по году
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

        # Фильтрация по жанрам
        if 'genres' in request.GET and request.GET.getlist('genres'):
            selected_genres = request.GET.getlist('genres')
            albums_query = albums_query.filter(genre__id__in=selected_genres)
            active_filters['selected_genres'] = selected_genres
        else:
            active_filters['selected_genres'] = []

        # Фильтрация по стилям
        if 'styles' in request.GET and request.GET.getlist('styles'):
            selected_styles = request.GET.getlist('styles')
            albums_query = albums_query.filter(styles__id__in=selected_styles).distinct()
            active_filters['selected_styles'] = selected_styles
        else:
            active_filters['selected_styles'] = []

        # Фильтрация по состоянию
        if 'conditions' in request.GET and request.GET.getlist('conditions'):
            selected_conditions = request.GET.getlist('conditions')
            albums_query = albums_query.filter(condition__in=selected_conditions)
            active_filters['selected_conditions'] = selected_conditions
        else:
            active_filters['selected_conditions'] = []

        # Фильтрация по формату издания
        if 'format_editions' in request.GET and request.GET.getlist('format_editions'):
            selected_format_editions = request.GET.getlist('format_editions')
            albums_query = albums_query.filter(format_edition__in=selected_format_editions)
            active_filters['selected_format_editions'] = selected_format_editions
        else:
            active_filters['selected_format_editions'] = []

        # Фильтрация по наличию
        if 'in_stock' in request.GET and request.GET['in_stock'] == '1':
            albums_query = albums_query.filter(stock__gt=0)
            active_filters['in_stock'] = True
        else:
            active_filters['in_stock'] = False

        # Фильтрация по предложению недели
        if 'offer_of_the_week' in request.GET and request.GET['offer_of_the_week'] == '1':
            albums_query = albums_query.filter(offer_of_the_week=True)
            active_filters['offer_of_the_week'] = True
        else:
            active_filters['offer_of_the_week'] = False

        # Устанавливаем текущие значения фильтров после обработки всех фильтров
        min_price = active_filters.get('min_price', min_price_default)
        max_price = active_filters.get('max_price', max_price_default)
        min_year = active_filters.get('min_year', min_year_default)
        max_year = active_filters.get('max_year', max_year_default)

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
        paginator = Paginator(albums_query, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'albums': page_obj,
            'genres': genres,
            'styles': styles,
            'conditions': conditions,
            'format_editions': format_editions,
            'min_price': f"{min_price:.2f}",
            'max_price': f"{max_price:.2f}",
            'min_year': min_year,
            'max_year': max_year,
            'min_price_default': min_price_default,
            'max_price_default': max_price_default,
            'min_year_default': min_year_default,
            'max_year_default': max_year_default,
            'selected_genres': active_filters.get('selected_genres', []),
            'selected_styles': active_filters.get('selected_styles', []),
            'selected_conditions': active_filters.get('selected_conditions', []),
            'selected_format_editions': active_filters.get('selected_format_editions', []),
            'in_stock': active_filters.get('in_stock', False),
            'offer_of_the_week': active_filters.get('offer_of_the_week', False),
            'selected_media_type': active_filters.get('selected_media_type', 'all'),
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
    model = Artist
    template_name = 'artist/artist_detail.html'
    slug_url_kwarg = 'artist_slug'
    context_object_name = 'artist'

class AlbumDetailView(CartMixin, views.generic.DetailView, NotificationsMixin):
    model = Album
    template_name = 'album/album_detail.html'
    slug_url_kwarg = 'album_slug'
    context_object_name = 'album'