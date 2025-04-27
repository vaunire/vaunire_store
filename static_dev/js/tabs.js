// Функция для активации вкладки
function activateTab(tabId) {
    // Удаляем активные классы
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active', 'bg-blue-50', 'text-blue-700');
        btn.classList.add('text-gray-600', 'bg-gray-50');
        const indicator = btn.querySelector('.active-indicator');
        if (indicator) indicator.classList.add('hidden');
        const svg = btn.querySelector('svg');
        if (svg) {
            svg.classList.remove('text-blue-700');
            svg.classList.add('text-gray-400');
        }
    });
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.add('hidden');
    });
    document.querySelectorAll('.tab-link').forEach(link => {
        link.classList.remove('active');
    });

    // Активируем нужную вкладку
    const targetButton = document.querySelector(`.tab-button[data-tab="${tabId}"]`);
    if (targetButton) {
        targetButton.classList.add('active', 'bg-blue-50', 'text-blue-700');
        targetButton.classList.remove('text-gray-600', 'bg-gray-50');
        const indicator = targetButton.querySelector('.active-indicator');
        if (indicator) indicator.classList.remove('hidden');
        const svg = targetButton.querySelector('svg');
        if (svg) {
            svg.classList.add('text-blue-700');
            svg.classList.remove('text-gray-400');
        }
    }

    const targetPane = document.getElementById(tabId);
    if (targetPane) {
        targetPane.classList.remove('hidden');
    }
    const targetLink = document.querySelector(`.tab-link[data-tab="${tabId}"]`);
    if (targetLink) {
        targetLink.classList.add('active');
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
        history.pushState({}, '', `/profile/${tabId}`);
    });
});

// Управление вкладками при клике на пункты выпадающего меню
document.querySelectorAll('.tab-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const tabId = link.dataset.tab;
        activateTab(tabId);
        history.pushState({}, '', `/profile/${tabId}`);
    });
});

// Проверка URL при загрузке страницы
window.addEventListener('load', () => {
    let path = window.location.pathname.split('/').filter(segment => segment).pop();
    const validTabs = ['account', 'orders', 'wishlist', 'returns'];
    const tabToActivate = validTabs.includes(path) ? path : 'account';

    console.log(`Initial tab: ${tabToActivate}`);
    activateTab(tabToActivate);

    if (!validTabs.includes(path)) {
        history.replaceState({}, '', '/profile/account');
    }

    // Проверяем параметр order_id для вкладки returns
    const urlParams = new URLSearchParams(window.location.search);
    const orderId = urlParams.get('order_id');
    if (orderId && tabToActivate === 'returns') {
        const targetTab = document.getElementById('returns');
        if (targetTab) {
            const returnRequest = targetTab.querySelector(`[data-order-id="${orderId}"]`);
            if (returnRequest) {
                setTimeout(() => {
                    returnRequest.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 100);
            }
        }
    }
});

// Обработка изменения истории браузера
window.addEventListener('popstate', () => {
    let path = window.location.pathname.split('/').filter(segment => segment).pop();
    const validTabs = ['account', 'orders', 'wishlist', 'returns'];
    const tabToActivate = validTabs.includes(path) ? path : 'account';

    activateTab(tabToActivate);

    // Проверяем параметр order_id при навигации
    const urlParams = new URLSearchParams(window.location.search);
    const orderId = urlParams.get('order_id');
    if (orderId && tabToActivate === 'returns') {
        const targetTab = document.getElementById('returns');
        if (targetTab) {
            const returnRequest = targetTab.querySelector(`[data-order-id="${orderId}"]`);
            if (returnRequest) {
                setTimeout(() => {
                    returnRequest.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 100);
            }
        }
    }
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