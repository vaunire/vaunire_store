document.querySelectorAll('[data-carousel]').forEach(carousel => {
    // Найти родительскую карточку
    const card = carousel.closest('.card');
    if (!card) {
        console.error('Card container not found for carousel:', carousel);
        return;
    }

    // Получаем изображения из data-images
    let images = [];
    try {
        images = JSON.parse(carousel.dataset.images);
    } catch (e) {
        console.error('Invalid JSON in data-images:', carousel.dataset.images, e);
        images = [carousel.querySelector('[data-carousel-image]').src];
    }

    // Получаем элементы карусели
    const totalImages = parseInt(carousel.dataset.totalImages, 10) || 1;
    const imageElements = carousel.querySelectorAll('[data-carousel-image]');
    const dotsContainer = card.querySelector('[data-carousel-dots]');
    const dotElements = dotsContainer ? dotsContainer.querySelectorAll('[data-dot-index]') : [];

    // Отладка
    console.log('Total images:', totalImages, 'Images:', images.length, 'Image elements:', imageElements.length, 'Dots:', dotElements.length);

    // Проверка загрузки изображений
    imageElements.forEach((img, index) => {
        img.addEventListener('error', () => console.error(`Failed to load image ${index + 1}: ${img.src}`));
        img.addEventListener('load', () => console.log(`Image ${index + 1} loaded: ${img.src}`));
    });

    // Если только одно изображение, отключаем карусель
    if (totalImages <= 1 || imageElements.length <= 1) {
        carousel.style.cursor = 'default';
        if (dotElements[0]) {
            dotElements[0].classList.add('bg-black/80');
            dotElements[0].classList.remove('bg-black/20');
        }
        return;
    }

    let currentIndex = 0;

    // Функция обновления карусели
    function updateCarousel(newIndex) {
        if (newIndex === currentIndex || newIndex < 0 || newIndex >= totalImages || !imageElements[newIndex]) {
            console.warn('Invalid index or no image element:', newIndex);
            return;
        }

        // Сбрасываем z-index текущего изображения
        imageElements[currentIndex].classList.remove('z-10');
        imageElements[currentIndex].classList.add('z-0');

        // Обновляем стиль текущей точки
        if (dotElements[currentIndex]) {
            dotElements[currentIndex].classList.remove('bg-black/80');
            dotElements[currentIndex].classList.add('bg-black/20');
        }

        // Показываем новое изображение
        currentIndex = newIndex;
        imageElements[currentIndex].classList.remove('z-0');
        imageElements[currentIndex].classList.add('z-10');

        // Обновляем стиль новой точки
        if (dotElements[currentIndex]) {
            dotElements[currentIndex].classList.remove('bg-black/20');
            dotElements[currentIndex].classList.add('bg-black/80');
        }

        // Отладка
        console.log(`Switched to image ${newIndex + 1}, Dot classes:`, dotElements[newIndex]?.classList.toString());
    }

    // Обработчик клика по точкам
    dotElements.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            console.log(`Clicked dot ${index + 1}`);
            updateCarousel(index);
        });
        // Поддержка клавиш для доступности
        dot.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                console.log(`Keydown on dot ${index + 1}`);
                updateCarousel(index);
            }
        });
    });

    // Обработчик наведения курсора
    carousel.addEventListener('mousemove', (e) => {
        const rect = carousel.getBoundingClientRect();
        const relativeX = e.clientX - rect.left;
        const width = rect.width;
        const zoneWidth = width / totalImages;
        const zoneIndex = Math.min(Math.floor(relativeX / zoneWidth), totalImages - 1);
        updateCarousel(zoneIndex);
    });

    // При уходе курсора возвращаем первое изображение
    carousel.addEventListener('mouseleave', () => {
        updateCarousel(0);
    });

    // Инициализация: подсвечиваем первую точку
    if (dotElements[0]) {
        dotElements[0].classList.remove('bg-black/20');
        dotElements[0].classList.add('bg-black/80');
        console.log('Initialized first dot as active');
    }

    // Инициализация: первое изображение на переднем плане
    if (imageElements[0]) {
        imageElements[0].classList.add('z-10');
    }
});