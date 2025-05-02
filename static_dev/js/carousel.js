document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-carousel]').forEach(carousel => {
        const card = carousel.closest('.card');
        if (!card) {
            console.error('Card container not found for carousel:', carousel);
            return;
        }

        let images = [];
        try {
            images = JSON.parse(carousel.dataset.images);
        } catch (e) {
            console.error('Invalid JSON in data-images:', carousel.dataset.images, e);
            images = [carousel.querySelector('[data-carousel-image]')?.src || ''];
        }

        const totalImages = parseInt(carousel.dataset.totalImages, 10) || 1;
        const imageElements = carousel.querySelectorAll('[data-carousel-image]');
        const dotsContainer = card.querySelector('[data-carousel-dots]');
        const dotElements = dotsContainer ? dotsContainer.querySelectorAll('[data-dot-index]') : [];

        if (totalImages !== imageElements.length) {
            console.error('Mismatch: totalImages and imageElements do not match');
        }
        if (totalImages !== dotElements.length) {
            console.error('Mismatch: totalImages and dotElements do not match');
        }

        if (!dotsContainer || dotElements.length === 0) {
            console.error('Dots container or dot elements not found');
            return;
        }

        if (totalImages <= 1) {
            if (dotElements[0]) {
                dotElements[0].classList.add('bg-black/80');
                dotElements[0].classList.remove('bg-black/20');
            }
            return;
        }

        let currentIndex = 0;

        function updateCarousel(newIndex) {
            if (newIndex < 0 || newIndex >= totalImages || !imageElements[newIndex]) {
                console.warn('Invalid index or no image element:', newIndex);
                return;
            }
            if (newIndex === currentIndex) return;

            // Сбрасываем все точки
            dotElements.forEach(dot => {
                dot.classList.remove('bg-black/80');
                dot.classList.add('bg-black/20');
            });

            // Сбрасываем z-index текущего изображения
            imageElements[currentIndex].classList.remove('z-10');
            imageElements[currentIndex].classList.add('z-0');

            // Обновляем индекс и изображение
            currentIndex = newIndex;
            imageElements[currentIndex].classList.remove('z-0');
            imageElements[currentIndex].classList.add('z-10');

            // Активируем текущую точку
            if (dotElements[currentIndex]) {
                dotElements[currentIndex].classList.remove('bg-black/20');
                dotElements[currentIndex].classList.add('bg-black/80');
            }
        }

        dotElements.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                updateCarousel(index);
            });
            dot.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    updateCarousel(index);
                }
            });
        });

        let debounceTimeout;
        carousel.addEventListener('mousemove', (e) => {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                const rect = carousel.getBoundingClientRect();
                const relativeX = e.clientX - rect.left;
                const width = rect.width;
                const zoneWidth = width / totalImages;
                const zoneIndex = Math.min(Math.floor(relativeX / zoneWidth), totalImages - 1);
                updateCarousel(zoneIndex);
            }, 100);
        });

        carousel.addEventListener('mouseleave', () => {
            updateCarousel(0);
        });

        if (dotElements[0]) {
            dotElements[0].classList.remove('bg-black/20');
            dotElements[0].classList.add('bg-black/80');
        }

        if (imageElements[0]) {
            imageElements[0].classList.add('z-10');
        }
    });
});