from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("catalog.urls")),
    path('catalog/', include("catalog.urls")),
    path('cart/', include("cart.urls")),
    path('orders/', include("orders.urls")),
    path('accounts/', include("accounts.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]

# Условие для режима отладки (DEBUG = True)
# Включается только в разработке, чтобы Django сам отдавал статические и медиафайлы
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)