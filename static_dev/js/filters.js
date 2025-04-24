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

// Обновление ползунка цены
function updatePriceSlider() {
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

    // Обновление полей ввода в реальном времени
    minInput.value = minValue;
    maxInput.value = maxValue;

    // Обновление полоски
    const minPercent = ((minValue - minLimit) / (maxLimit - minLimit)) * 100;
    const maxPercent = ((maxValue - minLimit) / (maxLimit - minLimit)) * 100;
    rangeTrack.style.left = `${minPercent}%`;
    rangeTrack.style.right = `${100 - maxPercent}%`;
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

    updatePriceSlider();
}

// Обновление ползунка года
function updateYearSlider() {
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

    // Обновление полей ввода в реальном времени
    minInput.value = minValue;
    maxInput.value = maxValue;

    // Обновление полоски
    const minPercent = ((minValue - minLimit) / (maxLimit - minLimit)) * 100;
    const maxPercent = ((maxValue - minLimit) / (maxLimit - minLimit)) * 100;
    rangeTrack.style.left = `${minPercent}%`;
    rangeTrack.style.right = `${100 - maxPercent}%`;
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

    updateYearSlider();
}

// Переключение видимости списка
function toggleList(listId, buttonId, toggleClass) {
    const list = document.getElementById(listId);
    const button = document.getElementById(buttonId);
    const items = document.querySelectorAll(`.${toggleClass}`);
    const filterContainer = document.querySelector('.filter-container');

    if (list.classList.contains('list-limited')) {
        // Открываем список
        list.classList.remove('list-limited');
        items.forEach(item => item.classList.remove('hidden'));
        button.textContent = 'Скрыть';

        // Убираем ограничение высоты контейнера
        filterContainer.style.maxHeight = 'none';
        filterContainer.style.overflowY = 'visible';
    } else {
        // Закрываем список
        list.classList.add('list-limited');
        items.forEach(item => item.classList.add('hidden'));
        button.textContent = 'Посмотреть все';

        // Возвращаем исходное состояние контейнера
        filterContainer.style.maxHeight = '';
        filterContainer.style.overflowY = 'auto';
    }
}

// Отправка формы
function submitForm(changedParams = {}) {
    const form = document.getElementById('filter-form');
    const formData = new FormData(form);
    const currentParams = new URLSearchParams(window.location.search);

    // Обновляем только измененные параметры
    for (const [key, value] of Object.entries(changedParams)) {
        if (value) {
            formData.set(key, value);
        } else {
            formData.delete(key);
        }
    }

    // Проверяем, изменились ли параметры
    let hasChanges = false;
    const newParams = new URLSearchParams(formData);
    for (const key of newParams.keys()) {
        if (newParams.get(key) !== currentParams.get(key)) {
            hasChanges = true;
            break;
        }
    }
    if (!hasChanges && currentParams.toString() !== newParams.toString()) {
        hasChanges = true;
    }

    // Отправляем форму только если есть изменения
    if (hasChanges) {
        const url = new URL(window.location.href);
        url.search = newParams.toString();
        window.location.href = url.toString();
    }
}

// Сброс формы
function resetForm() {
    const form = document.getElementById('filter-form');
    form.reset();
    updatePriceSlider();
    updateYearSlider();
    window.location.href = '/';
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    updatePriceSlider();
    updateYearSlider();

    // Дебонсер для текстовых полей
    const debouncedSubmit = debounce(submitForm, 300);

    // Обработчики для полей ввода цены
    document.getElementById('min_price').addEventListener('input', () => {
        syncPriceSlidersFromInputs();
        debouncedSubmit();
    });
    document.getElementById('max_price').addEventListener('input', () => {
        syncPriceSlidersFromInputs();
        debouncedSubmit();
    });

    // Обработчики для ползунков цены (обновление в реальном времени, отправка после отпускания)
    document.getElementById('min_price_range').addEventListener('input', updatePriceSlider);
    document.getElementById('max_price_range').addEventListener('input', updatePriceSlider);
    document.getElementById('min_price_range').addEventListener('change', submitForm);
    document.getElementById('max_price_range').addEventListener('change', submitForm);

    // Обработчики для полей ввода года
    document.getElementById('min_year').addEventListener('input', () => {
        syncYearSlidersFromInputs();
        debouncedSubmit();
    });
    document.getElementById('max_year').addEventListener('input', () => {
        syncYearSlidersFromInputs();
        debouncedSubmit();
    });

    // Обработчики для ползунков года (обновление в реальном времени, отправка после отпускания)
    document.getElementById('min_year_range').addEventListener('input', updateYearSlider);
    document.getElementById('max_year_range').addEventListener('input', updateYearSlider);
    document.getElementById('min_year_range').addEventListener('change', submitForm);
    document.getElementById('max_year_range').addEventListener('change', submitForm);

    // Обработчики для чекбоксов жанров и стилей
    document.querySelectorAll('input[name="genres"], input[name="styles"]').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            submitForm();
        });
    });

    // Обработчики для свича
    document.querySelectorAll('.in-stock-checkbox, .offer-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const isChecked = e.target.checked;
            const paramName = e.target.name;
            const paramValue = isChecked ? '1' : '';
            submitForm({ [paramName]: paramValue });
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