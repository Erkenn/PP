from django.contrib import admin
from .models import Genre, Platform, Game

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'rawg_id')
    search_fields = ('name',)

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'rawg_id')
    search_fields = ('name',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'rating', 'metacritic')
    list_filter = ('release_date',)
    search_fields = ('title', 'genres__name')
    filter_horizontal = ('genres', 'platforms')