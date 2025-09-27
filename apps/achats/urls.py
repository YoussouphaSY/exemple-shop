from django.urls import path
from . import views

app_name = 'achats'

urlpatterns = [
    path('', views.AchatListView.as_view(), name='list'),
    path('create/', views.AchatCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AchatDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.AchatUpdateView.as_view(), name='edit'),
    path('<int:pk>/recevoir/', views.RecevoirAchatView.as_view(), name='recevoir'),
    path('<int:pk>/facturer/', views.FacturerAchatView.as_view(), name='facturer'),
    path('fournisseurs/', views.FournisseurListView.as_view(), name='fournisseurs'),
    path('fournisseurs/create/', views.FournisseurCreateView.as_view(), name='fournisseur_create'),
    path('fournisseurs/quick-create/', views.FournisseurQuickCreateView.as_view(), name='fournisseur_quick_create'),
    path('fournisseurs/<int:pk>/', views.FournisseurDetailView.as_view(), name='fournisseur_detail'),
    path('export/', views.ExportAchatsView.as_view(), name='export'),
]