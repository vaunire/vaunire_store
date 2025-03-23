# Поддержка универсальных связей (Generic Relations) для связи с галереей изображений
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
# Модель ContentType для работы с универсальными связями
from django.contrib.contenttypes.models import ContentType

from django.db import models
from django.urls import reverse
from datetime import date
# slugify — функция для генерации URL-совместимых строк
from slugify import slugify

# mark_safe — делает строку безопасной для HTML (не экранирует теги, используется в админке)
from django.utils.safestring import mark_safe
# Пользовательская функция для загрузки изображений (определяет путь сохранения файлов)
from utils import upload_function


class MediaType(models.Model):

    # ❒ Модель для хранения типов медианосителей (CD, винил и т.д.)
    
    name = models.CharField(max_length = 100, verbose_name = 'Название медианосителя')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Медианоситель'
        verbose_name_plural = 'Медианосители'

class Member(models.Model):
    
    # ❒ Модель для хранения информации об участниках музыкальных групп или исполнителях

    first_name = models.CharField(max_length = 255, verbose_name = 'Имя музыканта')
    last_name = models.CharField(max_length = 255, verbose_name = 'Фамилия музыканта', blank = True, null = True)
    birth_date = models.DateField(verbose_name = 'Дата рождения', blank = True, null = True)
    role = models.CharField(max_length = 100, verbose_name = 'Роль в группе', blank = True, null = True)
    slug = models.SlugField(blank = True, help_text = 'Оставьте пустым для автозаполнения')
    image = models.ImageField(upload_to = upload_function, blank = True, null = True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def age(self, with_declension = True):
        # Вычисляет возраст музыканта на основе даты рождения
        if not self.birth_date:
            return None

        # Вычисляем возраст
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

        # Определяем склонение
        last_digit = age % 10
        last_two_digits = age % 100

        if last_two_digits in range(11, 15):
            return f"{age} лет"
        elif last_digit == 1:
            return f"{age} год"
        elif last_digit in [2, 3, 4]:
            return f"{age} года"
        else:
            return f"{age} лет"

    def save(self, *args, **kwargs):
        if not self.slug:  # Если slug пустой, генерируем его
            self.slug = slugify(self.name, lowercase = True)  
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Музыкант'
        verbose_name_plural = 'Музыканты'

class Genre(models.Model):
    
    # ❒ Модель для хранения типов музыкальных жанров, таких как Rock, Pop, Jazz и т.д.

    name = models.CharField(max_length = 50, verbose_name = 'Название жанра')
    slug = models.SlugField(blank = True, help_text = 'Оставьте пустым для автозаполнения')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug: 
            self.slug = slugify(self.name, lowercase = True) 
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

class Style(models.Model):

    # ❒ Модель для хранения музыкальных стилей, таких как Alternative Rock, Acoustic и т.д.

    name = models.CharField(max_length = 100, verbose_name = 'Название стиля')
    genre = models.ForeignKey(Genre, on_delete = models.CASCADE, verbose_name = 'Жанр', related_name = 'styles')
    slug = models.SlugField(blank = True, help_text = 'Оставьте пустым для автозаполнения')

    def __str__(self):
        return f"{self.name} ({self.genre.name})"
    
    def save(self, *args, **kwargs):
        if not self.slug:  
            self.slug = slugify(self.name, lowercase = True) 
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Стиль'
        verbose_name_plural = 'Стили'
        
class Artist(models.Model):
    
    # ❒ Модель для хранения информации о музыкальных исполнителях или группах

    name = models.CharField(max_length = 255, verbose_name = 'Исполнитель/группа')
    description = models.TextField(verbose_name = 'Описание', blank = True, null = True)
    country = models.CharField(max_length = 100, verbose_name = 'Страна', blank = True, null = True)
    genre = models.ForeignKey(Genre, verbose_name = 'Жанр', on_delete = models.CASCADE)
    members = models.ManyToManyField(Member, verbose_name = 'Участник', related_name = 'artist', blank = True)
    image_gallery = GenericRelation('ImageGallery', related_query_name = 'artists')
    image = models.ImageField(upload_to = upload_function, blank = True, null = True)
    slug = models.SlugField(blank = True, help_text = 'Оставьте пустым для автозаполнения')

    def __str__(self):
        return f"{self.name} | {self.genre.name}"
    
    # Возвращает URL для детальной страницы исполнителя
    def get_absolute_url(self):
        return reverse('artist_detail', kwargs = {'artist_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug: 
            self.slug = slugify(self.name, lowercase = True)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'

class Album(models.Model):

    # ❒ Модель для хранения информации о музыкальных альбомах

    name = models.CharField(max_length = 255, verbose_name = 'Название альбома')
    artist = models.ForeignKey(Artist, on_delete = models.CASCADE, verbose_name = 'Исполнитель')
    media_type = models.ForeignKey(MediaType, verbose_name = 'Тип медианосителя', on_delete = models.CASCADE)
    release_date = models.DateField(verbose_name = 'Дата релиза')
    genre = models.ForeignKey(Genre, on_delete = models.CASCADE, verbose_name = 'Жанр', blank = True, null = True)
    styles = models.ManyToManyField(Style, verbose_name = 'Стили', blank = True)
    tracklist = models.TextField(verbose_name = 'Трэклист', blank = True, null = True)
    description = models.TextField(verbose_name = 'Описание', default = 'Описание появится позже', blank = True, null = True) 
    label = models.CharField(max_length = 255, verbose_name = 'Лейбл', blank = True, null = True)
    country = models.CharField(max_length = 100, verbose_name ='Страна выпуска', blank = True, null = True)
    price = models.DecimalField(max_digits = 10, decimal_places = 2, verbose_name = 'Базовая цена', blank = True, null = True,
                                help_text = 'Если цена не указана, будет использоваться цена из активного прайс-листа.')
    condition = models.CharField(max_length = 50, verbose_name = 'Состояние товара', blank = True, null = True,
                                help_text = 'Например: Mint (идеальное), Near Mint (почти идеальное), Very Good (очень хорошее) и т.д.')
    article = models.CharField(max_length = 100, verbose_name = 'Артикул', unique = True)
    stock = models.PositiveIntegerField(default = 1, verbose_name = 'Наличие на складе')
    out_of_stock = models.BooleanField(default = False, verbose_name = "Нет в наличии", editable = False)
    offer_of_the_week = models.BooleanField(default = False, verbose_name = "Предложение недели")
    image = models.ImageField(upload_to = upload_function)
    slug = models.SlugField(blank = True, help_text = 'Оставьте пустым для автозаполнения')

    # Добавляем GenericRelation для связи с ImageGallery
    image_gallery = GenericRelation('ImageGallery', related_query_name = 'albums')

    format_quantity = models.CharField(max_length = 100, verbose_name = 'Количество носителей', blank = True, null = True,
                                       help_text = 'Примеры: "2xVinyl" (две виниловые пластинки), "1xCD" (один компакт-диск), "1xVinyl + 1xCD" (комбинированный набор)')
    format_type = models.CharField(max_length = 100, verbose_name = 'Тип формата', blank = True, null = True,
                                       help_text = 'Пример: LP (Long Play - полноформатный альбом), SP (Single Play - сингл), EP (Extended Play - мини альбом)')
    format_edition = models.CharField(max_length = 100, verbose_name = 'Издание', blank = True, null = True,
                                       help_text = 'Пример: Reissue (переиздание), Expanded Edition (расширенное издание), Limited Edition (ограниченное издание)')  
    format_color = models.CharField(max_length = 100, verbose_name = 'Цвет носителя', blank = True, null = True,
                                       help_text = 'Пример: White (белый), Black (чёрный), Transparent (прозрачный), Colored Vinyl (цветной винил)')  

    def __str__(self):
        return f"{self.id} | {self.artist.name} | {self.name}"

    # Формирует строку с описанием формата альбома (например, "2xVinyl, LP, Reissue, White")
    def get_format(self):
        return ', '.join([
            str(part) for part in [
                self.format_quantity,
                self.format_type,
                self.format_edition,
                self.format_color
            ] if part
        ])
    
    def get_absolute_url(self):
        # Возвращает URL для детальной страницы исполнителя
        return reverse('album_detail', kwargs = {'artist_slug': self.artist.slug, 'album_slug': self.slug})

    @property
    def ct_model(self):
        # Полезно для корзины, чтобы динамически определять тип товара (альбом, мерч и т.д.)
        return self._meta.model_name
    
    def save(self, *args, **kwargs):
        if not self.slug: 
            self.slug = slugify(self.name, lowercase = True)  
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        # Возвращает текущую цену альбома: из активного прайс-листа, если он есть, иначе базовую цену из поля price.
        from catalog.models import PriceList, PriceListItem
        active_pricelist = PriceList.objects.filter(is_active = True).first()
        if active_pricelist:
            pricelist_item = PriceListItem.objects.filter(
                price_list = active_pricelist,
                content_type = ContentType.objects.get_for_model(Album),
                object_id = self.id
            ).first()
            if pricelist_item:
                return pricelist_item.price
        return self.price if self.price is not None else 0

    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'
    
class PriceList(models.Model):

    # ❒ Модель для хранения информации о прайс-листах

    number = models.CharField(max_length = 50, unique = True, verbose_name = 'Номер прайс-листа') 
    start_date = models.DateField(verbose_name = 'Дата начала действия')
    end_date = models.DateField(blank = True, null = True, verbose_name = 'Дата окончания действия')
    is_active = models.BooleanField(default = True, verbose_name = 'Активен')

    def __str__(self):
        status = "Активен" if self.is_active else "Неактивен"
        return f'Прайс-лист №{self.number} от {self.start_date} ({status})'

    class Meta:
        verbose_name = 'Прайс-лист'
        verbose_name_plural = 'Прайс-листы'

class PriceListItem(models.Model):
    price_list = models.ForeignKey('PriceList', on_delete=models.CASCADE, related_name='items', verbose_name='Прайс-лист')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')

    MODEL_DISPLAY_NAME_MAP = {
        "album": {"is_constructable": True, "fields": ["artist.name", "name"], "separator": " - ", "prefix": "Альбом: ",
            "additional_fields": {
                "artist": "artist.name",
                "genre": "genre.name",
            }
        },
        # "service": {"is_constructable": False, "field": "name", "prefix": "Услуга: ", "additional_fields": { "genre": "category",}},
    }

    class Meta:
        verbose_name = 'Позиция прайс-листа'
        verbose_name_plural = 'Позиции прайс-листа'
        unique_together = ('price_list', 'content_type', 'object_id')

    def __str__(self):
        display_name = self.display_name()
        return f"{display_name} | {self.price} ({self.price_list.number})"

    def display_name(self):
        import operator
        model_name = self.content_type.model
        model_fields = self.MODEL_DISPLAY_NAME_MAP.get(model_name, {})
        if not model_fields:
            return str(self.content_object)

        prefix = model_fields.get("prefix", "")
        if model_fields.get("is_constructable", False):
            display_name = model_fields["separator"].join(
                [operator.attrgetter(field)(self.content_object) for field in model_fields["fields"]]
            )
        else:
            display_name = operator.attrgetter(model_fields["field"])(self.content_object)

        return f"{prefix}{display_name}"

    def get_additional_field(self, field_name):
        model_name = self.content_type.model
        model_fields = self.MODEL_DISPLAY_NAME_MAP.get(model_name, {})
        additional_fields = model_fields.get("additional_fields", {})
        field_path = additional_fields.get(field_name)
        if field_path:
            import operator
            try:
                if callable(getattr(self.content_object, field_path, None)):
                    return getattr(self.content_object, field_path)()
                return operator.attrgetter(field_path)(self.content_object) or "-"
            except (AttributeError, TypeError):
                return "-"
        return "-"

class ImageGallery(models.Model):
     
    # ❒ Модель для хранения изображений, связанных с разными объектами (альбомами, артистами и т.д.)

    content_type = models.ForeignKey(ContentType, on_delete = models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to = upload_function, verbose_name = 'Изображение')
    use_in_slider = models.BooleanField(default = False, verbose_name = 'Использовать в слайдере')

    def __str__(self):
            return f"Изображение для {self.content_object}"
    
    def image_url(self):
        # Отображает изображение в админке с помощью HTML-тега <img>
         return mark_safe(f'<img src = "{self.image.url}" width = "auto" height = "100px"')
    
    class Meta:
            verbose_name = 'Галерея изображений'
            verbose_name_plural = verbose_name

def check_stock_change(instance, **kwargs):
    # Проверяет наличие альбома на складе и обновляет поле out_of_stock
    try:
        album = Album.objects.get(id = instance.id)
    except Album.DoesNotExist:
        return None
    instance.out_of_stock = True if not album.stock else False
