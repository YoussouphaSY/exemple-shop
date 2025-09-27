from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('', views.StockListView.as_view(), name='list'),
    path('mouvements/', views.MouvementStockListView.as_view(), name='mouvements'),
    path('inventaire/', views.InventaireListView.as_view(), name='inventaire_list'),
    path('inventaire/create/', views.InventaireCreateView.as_view(), name='inventaire_create'),
    path('inventaire/<int:pk>/', views.InventaireDetailView.as_view(), name='inventaire_detail'),
    path('inventaire/<int:pk>/edit/', views.InventaireUpdateView.as_view(), name='inventaire_edit'),
    path('inventaire/<int:pk>/close/', views.InventaireCloseView.as_view(), name='inventaire_close'),
    path('ajustement/', views.AjustementStockView.as_view(), name='ajustement'),
]