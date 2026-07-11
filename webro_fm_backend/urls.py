from decouple import config
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Django admin panel hidden at an obscure path (change ADMIN_URL in .env to customize)
admin_url = config('ADMIN_URL', default='a8x9k2mz-admin/')
urlpatterns = [
    path(admin_url, admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('content.urls')),
    path('api/', include('interactions.urls')),
    path('api/', include('collaboration.urls')),
    path('api/', include('core.urls')),
]

# Serve static/media only in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
