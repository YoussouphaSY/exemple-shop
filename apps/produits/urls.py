from django.urls import path
from .views import (
    ProduitListView, ProduitDetailView, ProduitCreateView, ProduitUpdateView, ProduitDeleteView,
    CategorieListView, CategorieCreateView, ProduitQuickCreateView
)
from .quick_views import CategorieQuickCreateView

app_name = 'produits'

urlpatterns = [
    # Produits
    path('', ProduitListView.as_view(), name='list'),
    path('create/', ProduitCreateView.as_view(), name='create'),
    path('quick-create/', ProduitQuickCreateView.as_view(), name='quick_create'),
    path('<int:pk>/', ProduitDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', ProduitUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', ProduitDeleteView.as_view(), name='delete'),

    # Categories
    path('categories/', CategorieListView.as_view(), name='categories'),
    path('categories/create/', CategorieCreateView.as_view(), name='categorie_create'),
    path('categories/quick-create/', CategorieQuickCreateView.as_view(), name='categorie_quick_create'),
]