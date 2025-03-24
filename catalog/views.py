from django import views
from django.shortcuts import render

from .models import Album, Artist

class BaseView(views.View):
    def get(self, request, *args, **kwargs):
        albums = Album.objects.all().order_by('-id')[:5]
        context = {
            'albums': albums,
        }
        return render(request, 'base.html', context)

class ArtistDetailView(views.generic.DetailView):
    model = Artist
    template_name = 'artist/artist_detail.html'
    slug_url_kwarg = 'artist_slug'
    context_object_name = 'artist'

class AlbumDetailView(views.generic.DetailView):
    model = Album
    template_name = 'album/album_detail.html'
    slug_url_kwarg = 'album_slug'
    context_object_name = 'album'