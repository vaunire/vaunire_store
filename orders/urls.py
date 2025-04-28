from django.urls import path

from .views import MakeOrderView, SubmitReturnView, CancelReturnView

urlpatterns = [
    path('order/', MakeOrderView.as_view(), name = 'order'),
    path('<int:order_id>/return/', SubmitReturnView.as_view(), name = 'submit_return'),
    path('<int:return_id>/cancel/', CancelReturnView.as_view(), name = 'cancel_return'),
]