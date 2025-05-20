// Функция дебонсинга для ограничения частоты вызовов
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Хранилище для отслеживания текущих значений фильтров
let filterState = {
    min_price: null,
    max_price: null,
    min_year: null,
    max_year: null,
    in_stock: null,
    offer_of_the_week: null,
    genres: [],
    styles: [],
    min_price_default: null, // Добавляем для хранения фиксированного диапазона
    max_price_default: null
};

// Инициализация начального состояния фильтров
function initializeFilterState() {
    const urlParams = new URLSearchParams(window.location.search);

    // Получаем дефолтные значения из ползунков
    const minPriceDefault = parseInt(document.getElementById('min_price_range').min) || 0;
    const maxPriceDefault = parseInt(document.getElementById('max_price_range').max) || 10000;
    const minYearDefault = parseInt(document.getElementById('min_year_range').min) || 1900;
    const maxYearDefault = parseInt(document.getElementById('max_year_range').max) || 2025;

    // Сохраняем фиксированные значения
    filterState.min_price_default = minPriceDefault;
    filterState.max_price_default = maxPriceDefault;

    // Инициализируем filterState с проверкой валидности
    filterState.min_price = urlParams.get('min_price') ? parseInt(urlParams.get('min_price')) : null;
    filterState.max_price = urlParams.get('max_price') ? parseInt(urlParams.get('max_price')) : null;
    filterState.min_year = urlParams.get('min_year') ? parseInt(urlParams.get('min_year')) : null;
    filterState.max_year = urlParams.get('max_year') ? parseInt(urlParams.get('max_year')) : null;
    filterState.in_stock = urlParams.get('in_stock') === '1' ? '1' : null;
    filterState.offer_of_the_week = urlParams.get('offer_of_the_week') === '1' ? '1' : null;
    filterState.genres = urlParams.getAll('genres');
    filterState.styles = urlParams.getAll('styles');

    // Синхронизируем ползунки и поля ввода
    updatePriceSlider();
    updateYearSlider();
}

// Обновление ползунка цены
function updatePriceSlider(changed = false) {
    const minSlider = document.getElementById('min_price_range');
    const maxSlider = document.getElementById('max_price_range');
    const minInput = document.getElementById('min_price');
    const maxInput = document.getElementById('max_price');
    const rangeTrack = document.getElementById('price-range-track');

    let minValue = parseInt(minSlider.value);
    let maxValue = parseInt(maxSlider.value);
    const minLimit = parseInt(minSlider.min);
    const maxLimit = parseInt(maxSlider.max);

    // Предотвращение пересечения ползунков
    if (minValue > maxValue - 100) {
        if (minValue === parseInt(minInput.value)) {
            maxValue = minValue + 100;
            maxSlider.value = maxValue;
        } else {
            minValue = maxValue - 100;
            minSlider.value = minValue;
        }
    }

    // Обновление полей ввода
    minInput.value = minValue;
    maxInput.value = maxValue;

    // Обновление полоски
    const minPercent = ((minValue - minLimit) / (maxLimit - minLimit)) * 100;
    const maxPercent = ((maxValue - minLimit) / (maxLimit - minLimit)) * 100;
    rangeTrack.style.left = `${minPercent}%`;
    rangeTrack.style.right = `${100 - maxPercent}%`;

    // Обновляем filterState и отправляем форму, если изменено
    if (changed) {
        filterState.min_price = minValue !== filterState.min_price_default ? minValue : null;
        filterState.max_price = maxValue !== filterState.max_price_default ? maxValue : null;
        submitForm();
    }
}

// Синхронизация ползунков цены с полями ввода
function syncPriceSlidersFromInputs() {
    const minInput = document.getElementById('min_price');
    const maxInput = document.getElementById('max_price');
    const minSlider = document.getElementById('min_price_range');
    const maxSlider = document.getElementById('max_price_range');

    let minValue = parseInt(minInput.value) || parseInt(minSlider.min);
    let maxValue = parseInt(maxInput.value) || parseInt(maxSlider.max);

    minValue = Math.max(parseInt(minSlider.min), Math.min(minValue, parseInt(maxSlider.max)));
    maxValue = Math.max(parseInt(minSlider.min), Math.min(maxValue, parseInt(maxSlider.max)));

    if (minValue > maxValue - 100) {
        maxValue = minValue + 100;
    }

    minSlider.value = minValue;
    maxSlider.value = maxValue;

    filterState.min_price = minValue !== filterState.min_price_default ? minValue : null;
    filterState.max_price = maxValue !== filterState.max_price_default ? maxValue : null;
    updatePriceSlider(true);
}

// Обновление ползунка года
function updateYearSlider(changed = false) {
    const minSlider = document.getElementById('min_year_range');
    const maxSlider = document.getElementById('max_year_range');
    const minInput = document.getElementById('min_year');
    const maxInput = document.getElementById('max_year');
    const rangeTrack = document.getElementById('year-range-track');

    let minValue = parseInt(minSlider.value);
    let maxValue = parseInt(maxSlider.value);
    const minLimit = parseInt(minSlider.min);
    const maxLimit = parseInt(maxSlider.max);

    // Предотвращение пересечения ползунков
    if (minValue > maxValue - 1) {
        if (minValue === parseInt(minInput.value)) {
            maxValue = minValue + 1;
            maxSlider.value = maxValue;
        } else {
            minValue = maxValue - 1;
            minSlider.value = minValue;
        }
    }

    // Обновление полей ввода
    minInput.value = minValue;
    maxInput.value = maxValue;

    // Обновление полоски
    const minPercent = ((minValue - minLimit) / (maxLimit - minLimit)) * 100;
    const maxPercent = ((maxValue - minLimit) / (maxLimit - minLimit)) * 100;
    rangeTrack.style.left = `${minPercent}%`;
    rangeTrack.style.right = `${100 - maxPercent}%`;

    // Обновляем filterState и отправляем форму, если изменено
    if (changed) {
        filterState.min_year = minValue !== minLimit ? minValue : null;
        filterState.max_year = maxValue !== maxLimit ? maxValue : null;
        submitForm();
    }
}

// Синхронизация ползунков года с полями ввода
function syncYearSlidersFromInputs() {
    const minInput = document.getElementById('min_year');
    const maxInput = document.getElementById('max_year');
    const minSlider = document.getElementById('min_year_range');
    const maxSlider = document.getElementById('max_year_range');

    let minValue = parseInt(minInput.value) || parseInt(minSlider.min);
    let maxValue = parseInt(maxInput.value) || parseInt(maxSlider.max);

    minValue = Math.max(parseInt(minSlider.min), Math.min(minValue, parseInt(maxSlider.max)));
    maxValue = Math.max(parseInt(minSlider.min), Math.min(maxValue, parseInt(maxSlider.max)));

    if (minValue > maxValue - 1) {
        maxValue = minValue + 1;
    }

    minSlider.value = minValue;
    maxSlider.value = maxValue;

    filterState.min_year = minValue !== parseInt(minSlider.min) ? minValue : null;
    filterState.max_year = maxValue !== parseInt(maxSlider.max) ? maxValue : null;
    updateYearSlider(true);
}

// Переключение видимости списка
function toggleList(listId, buttonId, toggleClass) {
    const list = document.getElementById(listId);
    const button = document.getElementById(buttonId);
    const items = document.querySelectorAll(`.${toggleClass}`);
    const filterContainer = document.querySelector('.filter-container');

    if (list.classList.contains('list-limited')) {
        list.classList.remove('list-limited');
        items.forEach(item => item.classList.remove('hidden'));
        button.textContent = 'Скрыть';
        filterContainer.style.maxHeight = 'none';
        filterContainer.style.overflowY = 'visible';
    } else {
        list.classList.add('list-limited');
        items.forEach(item => item.classList.add('hidden'));
        button.textContent = 'Посмотреть все';
        filterContainer.style.maxHeight = '';
        filterContainer.style.overflowY = 'auto';
    }
}

// Отправка формы с фильтрацией параметров
function submitForm() {
    const newParams = new URLSearchParams();

    // Используем фиксированные дефолтные значения
    const minPriceDefault = filterState.min_price_default;
    const maxPriceDefault = filterState.max_price_default;
    const minYearDefault = parseInt(document.getElementById('min_year_range').min) || 1900;
    const maxYearDefault = parseInt(document.getElementById('max_year_range').max) || 2025;

    // Добавляем параметры цены, только если они отличаются от дефолтных
    if (filterState.min_price !== null && filterState.min_price !== minPriceDefault) {
        newParams.set('min_price', filterState.min_price);
    }
    if (filterState.max_price !== null && filterState.max_price !== maxPriceDefault) {
        newParams.set('max_price', filterState.max_price);
    }

    // Добавляем параметры года, только если они отличаются от дефолтных
    if (filterState.min_year !== null && filterState.min_year !== minYearDefault) {
        newParams.set('min_year', filterState.min_year);
    }
    if (filterState.max_year !== null && filterState.max_year !== maxYearDefault) {
        newParams.set('max_year', filterState.max_year);
    }

    // Добавляем жанры
    filterState.genres.forEach(genre => {
        newParams.append('genres', genre);
    });

    // Добавляем стили
    filterState.styles.forEach(style => {
        newParams.append('styles', style);
    });

    // Добавляем параметры переключателей
    if (filterState.in_stock) {
        newParams.set('in_stock', '1');
    }
    if (filterState.offer_of_the_week) {
        newParams.set('offer_of_the_week', '1');
    }

    // Сохраняем текущую страницу пагинации
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page');
    if (page) {
        newParams.set('page', page);
    }

    // Обновляем URL
    const url = new URL(window.location.href);
    url.search = newParams.toString();
    window.location.href = url.toString();
}

// Сброс формы
function resetForm() {
    const form = document.getElementById('filter-form');
    form.reset();
    filterState = {
        min_price: null,
        max_price: null,
        min_year: null,
        max_year: null,
        in_stock: null,
        offer_of_the_week: null,
        genres: [],
        styles: [],
        min_price_default: filterState.min_price_default,
        max_price_default: filterState.max_price_default
    };
    updatePriceSlider();
    updateYearSlider();
    window.location.href = '/';
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    initializeFilterState();

    // Дебонсер для текстовых полей
    const debouncedSubmit = debounce(submitForm, 300);

    // Обработчики для полей ввода цены
    document.getElementById('min_price').addEventListener('input', () => {
        syncPriceSlidersFromInputs();
    });
    document.getElementById('max_price').addEventListener('input', () => {
        syncPriceSlidersFromInputs();
    });

    // Обработчики для ползунков цены
    document.getElementById('min_price_range').addEventListener('input', () => updatePriceSlider());
    document.getElementById('max_price_range').addEventListener('input', () => updatePriceSlider());
    document.getElementById('min_price_range').addEventListener('change', () => updatePriceSlider(true));
    document.getElementById('max_price_range').addEventListener('change', () => updatePriceSlider(true));

    // Обработчики для полей ввода года
    document.getElementById('min_year').addEventListener('input', () => {
        syncYearSlidersFromInputs();
    });
    document.getElementById('max_year').addEventListener('input', () => {
        syncYearSlidersFromInputs();
    });

    // Обработчики для ползунков года
    document.getElementById('min_year_range').addEventListener('input', () => updateYearSlider());
    document.getElementById('max_year_range').addEventListener('input', () => updateYearSlider());
    document.getElementById('min_year_range').addEventListener('change', () => updateYearSlider(true));
    document.getElementById('max_year_range').addEventListener('change', () => updateYearSlider(true));

    // Обработчики для чекбоксов жанров и стилей
    document.querySelectorAll('input[name="genres"], input[name="styles"]').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            filterState.genres = Array.from(document.querySelectorAll('input[name="genres"]:checked')).map(cb => cb.value);
            filterState.styles = Array.from(document.querySelectorAll('input[name="styles"]:checked')).map(cb => cb.value);
            submitForm();
        });
    });

    // Обработчики для свича
    document.querySelectorAll('.in-stock-checkbox, .offer-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const isChecked = e.target.checked;
            const paramName = e.target.name;
            filterState[paramName] = isChecked ? '1' : null;
            submitForm();
        });
    });

    // Обработчики для кнопок "Посмотреть все"
    const toggleButtons = [
        { id: 'toggle-genres', list: 'genres-list', toggleClass: 'toggleable-genre' },
        { id: 'toggle-styles', list: 'styles-list', toggleClass: 'toggleable-style' }
    ];

    toggleButtons.forEach(({ id, list, toggleClass }) => {
        const button = document.getElementById(id);
        if (button) {
            button.addEventListener('click', () => toggleList(list, id, toggleClass));
        }
    });
});