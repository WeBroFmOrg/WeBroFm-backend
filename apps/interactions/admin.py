from django.contrib import admin
from .models import Favorite, ContinuePlaying, EpisodeHit

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'show', 'created_at')
    list_filter = ('created_at',)

@admin.register(ContinuePlaying)
class ContinuePlayingAdmin(admin.ModelAdmin):
    list_display = ('user', 'episode', 'last_position_seconds', 'updated_at')
    list_filter = ('updated_at',)

@admin.register(EpisodeHit)
class EpisodeHitAdmin(admin.ModelAdmin):
    list_display = ('episode', 'user', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    search_fields = ('ip_address', 'user_agent')
    ordering = ('-created_at',)
