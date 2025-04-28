document.addEventListener('DOMContentLoaded', function () {
    // Инициализация карты с обработкой ошибок
    ymaps.ready(initMap).catch(function (error) {
        showError('Не удалось загрузить карту. Проверьте подключение или API-ключ.');
        console.error('Ошибка загрузки Яндекс.Карт:', error);
    });

    // Объявление переменных для карты, метки и поиска
    let myMap = null;
    let placemark = null;
    let searchControl = null;
    const SAFU_ADDRESS = 'Архангельская область, Северодвинск, улица Капитана Воронина, 6';
    const SAFU_COORDS = [64.562961, 39.803955];

    // Основная функция инициализации карты
    function initMap() {
        try {
            myMap = new ymaps.Map("map", {
                center: [64.562961, 39.803955],
                zoom: 14,
                controls: ['zoomControl']
            });

            // Настройка поискового контрола
            searchControl = new ymaps.control.SearchControl({
                options: {
                    provider: 'yandex#search',
                    noPlacemark: true,
                    boundedBy: [[64.45, 39.70], [64.65, 39.95]],
                    placeholderContent: 'Введите адрес, включая подъезд и квартиру',
                    fitMaxWidth: true
                }
            });
            myMap.controls.add(searchControl);

            // Обработчик выбора результата поиска
            searchControl.events.add('resultselect', handleSearchResult);

            setDefaultOrderDate();
            checkBuyingTypeElement();
        } catch (error) {
            showError('Ошибка инициализации карты.');
            console.error('Ошибка initMap:', error);
        }
    }

    // Установка даты заказа по умолчанию (текущая дата + 2 дня)
    function setDefaultOrderDate() {
        try {
            const orderDateInput = document.getElementById('id_order_date');
            if (orderDateInput) {
                const today = new Date();
                const defaultDate = new Date(today);
                defaultDate.setDate(today.getDate() + 2);
                orderDateInput.value = defaultDate.toISOString().split('T')[0];
            }
        } catch (error) {
            console.error('Ошибка setDefaultOrderDate:', error);
        }
    }

    // Проверка и инициализация элемента выбора типа доставки
    function checkBuyingTypeElement() {
        try {
            const buyingTypeSelect = document.getElementById('id_buying_type');
            if (buyingTypeSelect) {
                initializeBuyingType(buyingTypeSelect);
            } else {
                setTimeout(checkBuyingTypeElement, 500);
            }
        } catch (error) {
            console.error('Ошибка checkBuyingTypeElement:', error);
        }
    }

    // Инициализация обработчика изменения типа доставки
    function initializeBuyingType(buyingTypeSelect) {
        try {
            handleBuyingTypeChange();
            buyingTypeSelect.addEventListener('change', handleBuyingTypeChange);
        } catch (error) {
            console.error('Ошибка initializeBuyingType:', error);
        }
    }

    // Установка адреса на карте с созданием метки
    function setAddress(address, coords, zoom = 17, isSafu = false) {
        try {
            console.log('Установка адреса:', address, 'Координаты:', coords);
            document.getElementById('address').value = address;
            document.getElementById('address-text').textContent = address;
            document.getElementById('error-message').style.display = 'none';

            if (placemark) {
                myMap.geoObjects.remove(placemark);
                placemark = null;
            }

            placemark = new ymaps.Placemark(coords, {
                balloonContent: address,
                iconCaption: isSafu ? 'ИСМАРТ' : ''
            });

            myMap.geoObjects.add(placemark);
            myMap.panTo(coords, { duration: 500 }).then(function () {
                myMap.setZoom(zoom, { duration: 300 });
            });
        } catch (error) {
            showError('Ошибка при установке адреса.');
            console.error('Ошибка setAddress:', error);
        }
    }

    // Обработчик клика по карте для установки адреса
    function handleMapClick(e) {
        try {
            const coords = e.get('coords');
            console.log('Клик по карте, координаты:', coords);
            ymaps.geocode(coords, { results: 1, provider: 'yandex#map' }).then(function (res) {
                const geoObject = res.geoObjects.get(0);
                if (geoObject) {
                    const fullAddress = geoObject.properties.get('text') || geoObject.properties.get('name') || 'Адрес не найден';
                    console.log('Адрес по клику:', fullAddress);
                    setAddress(fullAddress, coords);
                } else {
                    showError('Не удалось определить адрес.');
                }
            }).catch(function (error) {
                showError('Ошибка геокодирования. Проверьте API-ключ или подключение.');
                console.error('Ошибка геокодирования:', error);
            });
        } catch (error) {
            showError('Ошибка при обработке клика по карте.');
            console.error('Ошибка handleMapClick:', error);
        }
    }

    // Обработчик результатов поиска
    function handleSearchResult(e) {
        try {
            const index = e.get('index');
            console.log('Выбран результат поиска, индекс:', index);
            searchControl.getResult(index).then(function (res) {
                const properties = res.properties.getAll();
                console.log('Свойства результата поиска:', properties);
                // Пробуем получить полный адрес из text, description или name
                let fullAddress = properties.text || properties.description || properties.name || 'Адрес не найден';
                const coords = res.geometry.getCoordinates();
                console.log('Полный адрес:', fullAddress, 'Координаты:', coords);
                setAddress(fullAddress, coords);
            }).catch(function (error) {
                showError('Ошибка поиска адреса.');
                console.error('Ошибка поиска:', error);
            });
        } catch (error) {
            showError('Ошибка при обработке поиска.');
            console.error('Ошибка handleSearchResult:', error);
        }
    }

    // Обработчик изменения типа доставки (самовывоз/доставка)
    function handleBuyingTypeChange() {
        try {
            const buyingTypeSelect = document.getElementById('id_buying_type');
            if (!buyingTypeSelect) {
                showError('Ошибка: поле доставки не найдено.');
                return;
            }

            const buyingType = buyingTypeSelect.value;
            const mapContainer = document.getElementById('map');

            if (buyingType === 'self') {
                setAddress(SAFU_ADDRESS, SAFU_COORDS, 16, true);
                myMap.events.remove('click', handleMapClick);
                if (searchControl) {
                    myMap.controls.remove(searchControl);
                }
                myMap.behaviors.disable(['drag', 'scrollZoom']);
                mapContainer.classList.add('map-disabled');
            } else {
                myMap.events.add('click', handleMapClick);
                if (searchControl && !myMap.controls.get('searchControl')) {
                    myMap.controls.add(searchControl);
                }
                myMap.behaviors.enable(['drag', 'scrollZoom']);
                mapContainer.classList.remove('map-disabled');

                const currentAddress = document.getElementById('address').value;
                if (currentAddress === SAFU_ADDRESS) {
                    document.getElementById('address').value = '';
                    document.getElementById('address-text').textContent = 'Не выбран';
                    if (placemark) {
                        myMap.geoObjects.remove(placemark);
                        placemark = null;
                    }
                    myMap.setCenter([64.5635, 39.8302], 14);
                }
            }
        } catch (error) {
            showError('Ошибка при смене типа доставки.');
            console.error('Ошибка handleBuyingTypeChange:', error);
        }
    }

    // Обработчик отправки формы с валидацией
    document.getElementById('order-form').addEventListener('submit', function (e) {
        try {
            const address = document.getElementById('address').value;
            const agreement = document.getElementById('agreement').checked;
            const buyingType = document.getElementById('id_buying_type')?.value;

            if (!address) {
                e.preventDefault();
                showError('Выберите адрес на карте.');
                return;
            }

            if (buyingType === 'self' && address !== SAFU_ADDRESS) {
                e.preventDefault();
                showError('Для самовывоза адрес должен быть: Северодвинск, ул. Капитана Воронина, 6.');
                return;
            }

            if (!agreement) {
                e.preventDefault();
                showError('Необходимо согласиться с Политикой конфиденциальности.');
                return;
            }
        } catch (error) {
            e.preventDefault();
            showError('Ошибка при проверке формы.');
            console.error('Ошибка валидации формы:', error);
        }
    });

    // Функция отображения ошибок
    function showError(message) {
        const deepen = document.getElementById('error-message');
        if (deepen) {
            deepen.textContent = message;
            deepen.style.display = 'block';
        }
        console.error('Ошибка:', message);
    }
});