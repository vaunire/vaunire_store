from django.urls import path

from .views import CartView, AddToCartView, RemoveFromCartView, ChangeQuantityView

urlpatterns = [
    path('cart/', CartView.as_view(), name = 'cart'),
    path('add-to-cart/<str:ct_model>/<str:slug>/', AddToCartView.as_view(), name = 'add_to_cart'),
    path('remove-from-cart/<str:ct_model>/<str:slug>/', RemoveFromCartView.as_view(), name = 'remove_from_cart'),
    path('change-qty/<str:ct_model>/<str:slug>/', ChangeQuantityView.as_view(), name = 'change_quantity'),
]