from django.urls import path

from .views import AlbumDetailView, ArtistDetailView, BaseView

urlpatterns = [
    path('', BaseView.as_view(), name = 'base'),
    path('<str:artist_slug>/', ArtistDetailView.as_view(), name = 'artist_detail'),
    path('<str:artist_slug>/<str:album_slug>/', AlbumDetailView.as_view(), name = 'album_detail'),
]