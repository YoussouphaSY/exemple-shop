"""
URL configuration for shop360 project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from apps.dashboard.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('apps.users.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('produits/', include('apps.produits.urls')),
    path('stock/', include('apps.stock.urls')),
    path('ventes/', include('apps.ventes.urls')),
    path('achats/', include('apps.achats.urls')),
    path('finance/', include('apps.finance.urls')),
    path('api/', include([
        path('produits/', include('apps.produits.api_urls')),
        path('stock/', include('apps.stock.api_urls')),
        path('ventes/', include('apps.ventes.api_urls')),
        path('achats/', include('apps.achats.api_urls')),
        path('finance/', include('apps.finance.api_urls')),
        path('dashboard/', include('apps.dashboard.api_urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)