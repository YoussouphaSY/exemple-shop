from django.urls import path
from . import views

app_name = 'ventes'

urlpatterns = [
    path('', views.VenteListView.as_view(), name='list'),
    path('create/', views.VenteCreateView.as_view(), name='create'),
    path('<int:pk>/', views.VenteDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.VenteUpdateView.as_view(), name='edit'),
    path('<int:pk>/ticket/', views.TicketView.as_view(), name='ticket'),
    path('<int:pk>/finalize/', views.FinalizeVenteView.as_view(), name='finalize'),
    path('caisse/', views.CaisseView.as_view(), name='caisse'),
    path('dettes/', views.DettesListView.as_view(), name='dettes'),
    path('<int:pk>/payment/', views.EnregistrerPaiementView.as_view(), name='enregistrer_paiement'),
    path('export/', views.ExportVentesView.as_view(), name='export'),
]