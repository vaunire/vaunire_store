from django.urls import path

from .views import CheckoutView, MakeOrderView

urlpatterns = [
    path('order/', MakeOrderView.as_view(), name = 'order'),
    path('checkout/', CheckoutView.as_view(), name = 'checkout')
]