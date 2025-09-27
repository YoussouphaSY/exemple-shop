from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.FinanceOverviewView.as_view(), name='overview'),
    path('transactions/', views.TransactionListView.as_view(), name='transactions'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_edit'),
    path('budgets/', views.BudgetListView.as_view(), name='budgets'),
    path('budgets/create/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('budgets/<int:pk>/', views.BudgetDetailView.as_view(), name='budget_detail'),
    path('budgets/<int:pk>/edit/', views.BudgetUpdateView.as_view(), name='budget_edit'),
    path('caisse/', views.CaisseView.as_view(), name='caisse'),
    path('caisse/mouvement/', views.MouvementCaisseView.as_view(), name='mouvement_caisse'),
    path('export/', views.ExportFinanceView.as_view(), name='export'),
    path('rapport/', views.RapportFinancierView.as_view(), name='rapport'),
]