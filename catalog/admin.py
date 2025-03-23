from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import MultipleRelatedDropdownFilter, RelatedDropdownFilter, RangeDateFilter
from unfold.contrib.forms.widgets import WysiwygWidget
from django.urls import reverse
from django.utils.html import format_html

from .models import Album, Artist, Genre, ImageGallery, MediaType, Member, Style, PriceList, PriceListItem


class BaseAdmin(ModelAdmin):
    list_filter_submit = True 
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},  
    }


class PriceListItemInLine(TabularInline):
    model = PriceListItem
    extra = 1
    fields = ('content_type', 'object_id', 'content_object_link', 'artist', 'genre', 'price')
    readonly_fields = ('content_object_link', 'artist', 'genre')

    def content_object_link(self, obj):
        if obj.content_object:
            url = reverse(
                f"admin:{obj.content_type.app_label}_{obj.content_type.model}_change",
                args=[obj.object_id]
            )
            return format_html('<a href="{}">{}</a>', url, obj.display_name())
        return "-"
    content_object_link.short_description = 'Товар'

    def artist(self, obj):
        return obj.get_additional_field('artist')
    artist.short_description = 'Исполнитель'

    def genre(self, obj):
        return obj.get_additional_field('genre')
    genre.short_description = 'Жанр/Категория'


class MembersInLine(TabularInline):
    model = Artist.members.through  
    verbose_name = 'Участник'
    verbose_name_plural = 'Участники'


class ImageGalleryInLine(GenericTabularInline):
    model = ImageGallery 
    readonly_fields = ('image_url',)  


@admin.register(MediaType)
class MediaTypeAdmin(BaseAdmin):
    list_display = ('name',)  
    search_fields = ('name',) 
    list_filter = ()  


@admin.register(Genre)
class GenreAdmin(BaseAdmin):
    list_display = ('name',)  
    search_fields = ('name',) 
    list_filter = () 


@admin.register(Style)
class StyleAdmin(BaseAdmin):
    list_display = ('name', 'genre')  
    search_fields = ('name', 'genre__name') 
    list_filter = (
        ('genre', RelatedDropdownFilter),  
    )


@admin.register(Artist)
class ArtistAdmin(BaseAdmin):
    list_display = ('name', 'genre', 'country') 
    search_fields = ('name', 'genre__name') 
    list_filter = (
        ('genre', RelatedDropdownFilter), 
        'country', 
        ('members', MultipleRelatedDropdownFilter), 
    )
    inlines = [MembersInLine, ImageGalleryInLine]
    exclude = ('members',)  


@admin.register(Member)
class MemberAdmin(BaseAdmin):
    list_display = ('__str__', 'age', 'get_artists') 
    search_fields = ('first_name', 'last_name', 'artist__name') 
    list_filter = (
        ('artist', MultipleRelatedDropdownFilter),  
    )

    def age(self, obj):
        if not obj.birth_date:
            return "-"
        months = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
        ]
        day = obj.birth_date.day
        month = months[obj.birth_date.month - 1]
        year = obj.birth_date.year
        birth_date_str = f"{day} {month} {year}"
        return f"{birth_date_str}"
    age.short_description = 'Дата рождения'

    def get_artists(self, obj):
        through_model = Artist.members.through
        artist_members = through_model.objects.filter(member=obj)
        artists = Artist.objects.filter(id__in=artist_members.values('artist_id'))
        if artists:
            return ", ".join(artist.name for artist in artists)
        return "-"
    get_artists.short_description = 'Исполнитель/Группа' 


@admin.register(Album)
class AlbumAdmin(BaseAdmin):
    list_display = ('name', 'artist', 'release_date', 'price', 'stock')  
    search_fields = ('name', 'artist__name')  
    list_filter = (
        'release_date',  
        ('artist', RelatedDropdownFilter), 
        ('genre', RelatedDropdownFilter),  
        ('media_type', RelatedDropdownFilter),  
        ('styles', MultipleRelatedDropdownFilter),  
        'country', 
        'condition',  
        'out_of_stock', 
        'offer_of_the_week',  
    )
    inlines = [ImageGalleryInLine]

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'name',
                'artist',
                'release_date',
                'label',
                'country',
                'media_type',
            )
        }),
        ('Жанр и стили', {
            'fields': (
                'genre',
                'styles',
            )
        }),
        ('Формат альбома', {
            'fields': (
                'format_type',
                'format_color',
                'format_edition',
                'format_quantity',
            )
        }),
        ('Описание и треклист', {
            'fields': (
                'description',
                'tracklist',
            )
        }),
        ('Цена и наличие', {
            'fields': (
                'price',
                'condition',
                'stock',
                'offer_of_the_week', 
            )
        }),
        ('Дополнительная информация', {
            'fields': (
                'article',
                'image',
                'slug',
            )
        }),
    )


@admin.register(PriceList)
class PriceListAdmin(BaseAdmin):
    list_display = ('number', 'start_date', 'end_date', 'is_active')  
    search_fields = ('number',)  
    list_filter = (
        'is_active',
        ('start_date', RangeDateFilter),
    )
    inlines = [PriceListItemInLine]


@admin.register(PriceListItem)
class PriceListItemAdmin(BaseAdmin):
    list_display = ('display_name', 'artist', 'genre', 'price_list', 'price')
    search_fields = ('price_list__number', 'content_object__name', 'content_object__artist__name')  
    list_filter = (
        ('price_list', RelatedDropdownFilter),
        'content_type',
    )
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'price_list',
                'content_type',
                'object_id',
                'price',
            )
        }),
        ('Информация о товаре', {
            'fields': (
                'content_object_link',
                'display_artist',
                'display_genre',
            ),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('content_object_link', 'display_artist', 'display_genre')

    def content_object_link(self, obj):
        if obj.content_object:
            url = reverse(
                f"admin:{obj.content_type.app_label}_{obj.content_type.model}_change",
                args=[obj.object_id]
            )
            return format_html('<a href="{}">{}</a>', url, obj.display_name())
        return "-"
    content_object_link.short_description = 'Товар'

    def display_name(self, obj):
        return obj.display_name()
    display_name.short_description = 'Товар'

    def artist(self, obj):
        return obj.get_additional_field('artist')
    artist.short_description = 'Исполнитель'

    def genre(self, obj):
        return obj.get_additional_field('genre')
    genre.short_description = 'Жанр/Категория'

    def display_artist(self, obj):
        return obj.get_additional_field('artist')
    display_artist.short_description = 'Исполнитель'

    def display_genre(self, obj):
        return obj.get_additional_field('genre')
    display_genre.short_description = 'Жанр/Категория'

    def display_format(self, obj):
        return obj.get_additional_field('format')
    display_format.short_description = 'Формат'


@admin.register(ImageGallery)
class ImageGalleryAdmin(BaseAdmin):
    list_display = ('content_object', 'use_in_slider')  
    search_fields = ('content_object__name',)  
    list_filter = (
        'use_in_slider', 
    )