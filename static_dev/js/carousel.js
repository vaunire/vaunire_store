document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-carousel]').forEach(carousel => {
        const card = carousel.closest('.card');
        if (!card) {
            console.error('Контейнер карточки не найден для карусели:', carousel);
            return;
        }

        let images = [];
        try {
            const cleanedDataImages = carousel.dataset.images.replace(/\s+/g, ' ').trim();
            images = JSON.parse(cleanedDataImages).filter(url => url && url !== '');
        } catch (e) {
            console.error('Некорректный JSON в data-images:', carousel.dataset.images, e);
            images = [carousel.querySelector('[data-carousel-image]')?.src || '/static/images/placeholder.jpg'];
        }

        const totalImages = parseInt(carousel.dataset.totalImages, 10) || 1;
        const imageElements = carousel.querySelectorAll('[data-carousel-image]');
        const dotsContainer = card.querySelector('[data-carousel-dots]');
        const dotElements = dotsContainer ? dotsContainer.querySelectorAll('[data-dot-index]') : [];

        if (totalImages !== imageElements.length) {
            console.error(`Несоответствие: totalImages (${totalImages}) и imageElements (${imageElements.length})`);
            return;
        }
        if (totalImages !== dotElements.length) {
            console.warn(`Несоответствие: totalImages (${totalImages}) и dotElements (${dotElements.length})`);
            dotElements.forEach((dot, index) => {
                if (index >= totalImages) {
                    dot.style.display = 'none';
                }
            });
        }
        if (!dotsContainer || dotElements.length === 0) {
            console.error('Контейнер точек или сами точки не найдены');
            return;
        }

        if (totalImages <= 1) {
            if (dotElements[0]) {
                dotElements[0].classList.add('bg-black');
                dotElements[0].classList.remove('bg-black/20');
                dotElements[0].setAttribute('aria-selected', 'true');
                console.log('Режим одного изображения: применен bg-black к первой точке');
            }
            return;
        }

        let currentIndex = 0;

        function updateCarousel(newIndex) {
            if (newIndex < 0 || newIndex >= totalImages || !imageElements[newIndex]) {
                console.warn('Некорректный индекс или нет элемента изображения:', newIndex);
                return;
            }

            // Сбрасываем стили всех точек
            dotElements.forEach((dot, index) => {
                dot.classList.remove('bg-black');
                dot.classList.add('bg-black/20');
                dot.setAttribute('aria-selected', 'false');
                console.log(`Сброс точки ${index} на bg-black/20`);
            });

            // Сбрасываем z-index всех изображений
            imageElements.forEach(img => {
                img.classList.remove('z-10');
                img.classList.add('z-0');
            });

            // Обновляем текущий индекс и стили
            currentIndex = newIndex;
            imageElements[currentIndex].classList.remove('z-0');
            imageElements[currentIndex].classList.add('z-10');

            if (dotElements[currentIndex]) {
                dotElements[currentIndex].classList.remove('bg-black/20');
                dotElements[currentIndex].classList.add('bg-black');
                dotElements[currentIndex].setAttribute('aria-selected', 'true');
                console.log(`Обновлена точка ${currentIndex} на bg-black`);
            } else {
                console.error(`Точка для индекса ${currentIndex} не найдена`);
            }
        }

        dotElements.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                console.log(`Нажата точка: индекс ${index}, классы до: ${dot.className}`);
                updateCarousel(index);
                console.log(`Классы после: ${dot.className}`);
            });
            dot.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    console.log(`Клавиша для точки: индекс ${index}`);
                    updateCarousel(index);
                }
            });
        });

        let isProcessing = false;
        const rect = carousel.getBoundingClientRect();
        const width = rect.width;
        const zoneWidth = width / totalImages;

        carousel.addEventListener('mousemove', (e) => {
            if (isProcessing) return;
            isProcessing = true;
            requestAnimationFrame(() => {
                const relativeX = e.clientX - rect.left;
                const zoneIndex = Math.min(Math.floor(relativeX / zoneWidth), totalImages - 1);
                updateCarousel(zoneIndex);
                isProcessing = false;
            });
        });

        carousel.addEventListener('mouseleave', () => {
            console.log('Мышь покинула карусель, возврат к индексу 0');
            updateCarousel(0);
        });

        // Инициализация
        imageElements[0].classList.add('z-10');
        if (dotElements[0]) {
            dotElements[0].classList.add('bg-black');
            dotElements[0].classList.remove('bg-black/20');
            dotElements[0].setAttribute('aria-selected', 'true');
        }
        updateCarousel(0);
    });
});