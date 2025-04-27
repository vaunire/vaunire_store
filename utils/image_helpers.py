class ImageUploadHelper:
    """ 
    Вспомогательный класс для генерации путей загрузки изображений.
    Динамически создаёт пути на основе поля модели (например, slug) и типа модели (Member, Artist, Album).
    """
    # Словарь настроек для разных моделей
    # Определяет, какое поле использовать для пути и в какую папку сохранять изображения
    FIELD_TO_COMBINE_MAP = {
        'defaults': {
            'upload_postfix': 'uploads'  # Папка по умолчанию, если модель не указана
        },
        'Member': {
            'field': 'slug',             # Поле модели для создания пути
            'upload_postfix': 'members_images'  # Название папки для хранения изображений
        },
        'Artist': {
            'field': 'slug',            
            'upload_postfix': 'artists_images'  
        },
        'Album': {
            'field': 'slug',            
            'upload_postfix': 'albums_images'   
        },
        'ReturnRequest': {
            'field': 'order.customer.user.username',
            'upload_postfix': 'customer_returns'
        }
    }

    def __init__(self, field_name_to_combine, instance, filename, upload_postfix):
        """
        Инициализация объекта для генерации пути.

        Args:
            field_name_to_combine (str): Имя поля модели, используемого для пути (например, 'slug').
            instance (Model): Экземпляр модели (Member, Artist, Album и т.д.).
            filename (str): Имя файла изображения (например, "image.jpg").
            upload_postfix (str): Постфикс для папки загрузки (например, "members_images").
        """
        self.field_name_to_combine = field_name_to_combine
        self.instance = instance
        self.extention = filename.split('.')[-1]  # Извлекаем расширение файла (например, "jpg")
        self.upload_postfix = f"{upload_postfix}"  # Устанавливаем постфикс для папки

    @classmethod
    def get_field_to_combine_and_upload_postfix(cls, klass):
        """
        Возвращает поле для генерации пути и постфикс для папки на основе имени модели.

        Args:
            klass (str): Имя класса модели (например, 'Member', 'Artist', 'Album').

        Returns:
            tuple: Кортеж (field_to_combine, upload_postfix), где: 
                - field_to_combine: поле для пути (например, 'slug').
                - upload_postfix: постфикс папки (например, 'members_images').
        """
        # Получаем поле для генерации пути из настроек модели
        field_to_combine = cls.FIELD_TO_COMBINE_MAP[klass]['field']
        # Получаем постфикс, если он есть, или используем значение по умолчанию
        upload_postfix = cls.FIELD_TO_COMBINE_MAP.get(
            'upload_postfix', cls.FIELD_TO_COMBINE_MAP['defaults']['upload_postfix']
        )
        return field_to_combine, upload_postfix

    @property
    def path(self):
        """
        Генерирует путь для сохранения изображения.

        Returns:
            str: Путь в формате "images/<модель>/<постфикс>/<значение_поля>.<расширение>".
            Пример: "images/member/members_images/Thom_Yorke/Thom_Yorke.jpg".
        """
        # Поддержка вложенных полей (например, customer.user.username)
        field_parts = self.field_name_to_combine.split('.')
        field_value = self.instance
        for part in field_parts:
            field_value = getattr(field_value, part)
        # Формируем имя файла: <значение_поля>.<расширение> 
        filename = '.'.join([field_value, self.extention])
        # Формируем полный путь: images/<имя_модели><постфикс>/<значение_поля>/<имя_файла>
        return f"images/{self.instance.__class__.__name__.lower()}/{self.upload_postfix}/{field_value}/{filename}"


def upload_function(instance, filename):
    """
    Функция для загрузки изображений, используется в поле `upload_to` модели.

    Args:
        instance (Model): Экземпляр модели, к которому привязан файл.
        filename (str): Имя файла изображения (например, "image.jpg").

    Returns:
        str: Путь для сохранения файла (например, "images/artist/artists_images/Hudson_Lee/Hudson_Lee.jpg").
    """
    # Если у экземпляра есть content_object (для Generic Relations), используем его
    if hasattr(instance, 'content_object'):
        instance = instance.content_object

    # Получаем поле для пути и постфикс папки на основе модели
    field_to_combine, upload_postfix = ImageUploadHelper.get_field_to_combine_and_upload_postfix(
        instance.__class__.__name__
    )

    # Создаём объект ImageUploadHelper и возвращаем сгенерированный путь
    image = ImageUploadHelper(field_to_combine, instance, filename, upload_postfix)
    return image.path