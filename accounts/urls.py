from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import AccountView, LoginView, RegistrationView, ClearNotificationsView, AddToWishlist, RemoveFromWishlist

urlpatterns = [
    path('login/', LoginView.as_view(), name = 'login'),
    path('registration/', RegistrationView.as_view(), name = 'registration'),
    path('logout/', LogoutView.as_view(next_page = '/'), name = 'logout'),
    path('profile/', AccountView.as_view(), name = 'account'),
    path('clear-notifications/', ClearNotificationsView.as_view(), name = 'clear_notifications'),
    path('add-to-wishlist/<int:album_id>/', AddToWishlist.as_view(), name = 'add_to_wishlist'),
    path('remove-from-wishlist/<int:album_id>/', RemoveFromWishlist.as_view(), name = 'remove_from_wishlist'),
]