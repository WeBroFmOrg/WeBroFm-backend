from django.contrib import admin
from .models import Language, Category, Author, Show, Episode

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    prepopulated_fields = {'code': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_featured', 'is_trending')
    list_filter = ('category', 'is_featured', 'is_trending')
    search_fields = ('title', 'description')

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'show', 'sequence_number', 'duration_seconds')
    list_filter = ('show',)
    search_fields = ('title', 'description')
