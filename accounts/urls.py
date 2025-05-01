from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views
from .views import (AccountView, AddToFavorite, AddToWishlist,
                    ClearNotificationsView, FavoritesView, LoginView,
                    RegistrationView, RemoveFromFavorite, RemoveFromWishlist,
                    UpdateProfileView)

urlpatterns = [
    path('', AccountView.as_view(), name = 'account'),
    path('<str:tab>/', AccountView.as_view(), name = 'account_tab'),

    path('my/favorites/', FavoritesView.as_view(), name = 'favorites'),

    path('sign/in/', LoginView.as_view(), name = 'login'),
    path('sign/up/', RegistrationView.as_view(), name = 'registration'),
    path('sign/out/', LogoutView.as_view(next_page = '/'), name = 'logout'),

    path('actions/clear-notifications/', ClearNotificationsView.as_view(), name = 'clear_notifications'),
    path('actions/profile-update/', UpdateProfileView.as_view(), name = 'update_profile'),

    path('actions/add-to-wishlist/<int:album_id>/', AddToWishlist.as_view(), name = 'add_to_wishlist'),
    path('actions/remove-from-wishlist/<int:album_id>/', RemoveFromWishlist.as_view(), name = 'remove_from_wishlist'),

    path('actions/add-to-favorite/<int:album_id>/', AddToFavorite.as_view(), name = 'add_to_favorite'),
    path('actions/remove-from-favorite/<int:album_id>/', RemoveFromFavorite.as_view(), name = 'remove_from_favorite'),
]