from django.urls import path
from . import views

app_name = 'produits'

urlpatterns = [
    path('', views.ProduitListView.as_view(), name='list'),
    path('create/', views.ProduitCreateView.as_view(), name='create'),
    path('quick-create/', views.ProduitQuickCreateView.as_view(), name='quick_create'),
    path('<slug:slug>/', views.ProduitDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.ProduitUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.ProduitDeleteView.as_view(), name='delete'),
    path('categories/', views.CategorieListView.as_view(), name='categories'),
    path('categories/create/', views.CategorieCreateView.as_view(), name='category_create'),
]