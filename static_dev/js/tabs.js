// Функция для активации вкладки
function activateTab(tabId) {
    // Удаляем активные классы
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active', 'bg-blue-50', 'text-blue-700');
        btn.classList.add('text-gray-600', 'bg-gray-50');
        btn.querySelector('.active-indicator').classList.add('hidden');
        btn.querySelector('svg').classList.remove('text-blue-700');
        btn.querySelector('svg').classList.add('text-gray-400');
    });
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.add('hidden');
    });

    // Активируем нужную вкладку
    const targetButton = document.querySelector(`.tab-button[data-tab="${tabId}"]`);
    if (targetButton) {
        targetButton.classList.add('active', 'bg-blue-50', 'text-blue-700');
        targetButton.classList.remove('text-gray-600', 'bg-gray-50');
        targetButton.querySelector('.active-indicator').classList.remove('hidden');
        targetButton.querySelector('svg').classList.add('text-blue-700');
        targetButton.querySelector('svg').classList.remove('text-gray-400');
        document.getElementById(tabId).classList.remove('hidden');
    }

    // Обновляем последний элемент хлебных крошек
    const breadcrumbLast = document.getElementById('breadcrumb-last');
    const tabTitles = {
        'account': 'Данные аккаунта',
        'orders': 'Мои заказы',
        'wishlist': 'Лист ожидания',
        'returns': 'Мои возвраты'
    };
    if (breadcrumbLast) {
        breadcrumbLast.textContent = tabTitles[tabId] || 'Данные аккаунта';
    }
}

// Управление вкладками при клике на кнопки вкладок
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabId = button.dataset.tab;
        activateTab(tabId);
        // Обновляем URL без хэша
        history.pushState({}, '', `/profile/${tabId}`);
    });
});

// Управление вкладками при клике на пункты выпадающего меню
document.querySelectorAll('.tab-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault(); // Предотвращаем перезагрузку страницы
        const tabId = link.dataset.tab;
        activateTab(tabId);
        // Обновляем URL без хэша
        history.pushState({}, '', `/profile/${tabId}`);
    });
});

// Проверка URL при загрузке страницы
window.addEventListener('load', () => {
    // Извлекаем tab из URL
    let path = window.location.pathname.split('/').filter(segment => segment).pop();
    const validTabs = ['account', 'orders', 'wishlist', 'returns'];

    // Если path не является валидной вкладкой, устанавливаем 'account'
    const tabToActivate = validTabs.includes(path) ? path : 'account';

    console.log(`Initial tab: ${tabToActivate}`); // Отладка
    activateTab(tabToActivate);

    // Если URL некорректный, обновляем его
    if (!validTabs.includes(path)) {
        history.replaceState({}, '', '/profile/account');
    }
});

// Обработка изменения истории браузера (навигация вперед/назад)
window.addEventListener('popstate', () => {
    let path = window.location.pathname.split('/').filter(segment => segment).pop();
    const validTabs = ['account', 'orders', 'wishlist', 'returns'];
    const tabToActivate = validTabs.includes(path) ? path : 'account';

    activateTab(tabToActivate);
});

// Управление модальными окнами
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}