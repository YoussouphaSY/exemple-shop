from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('api/charts/', views.ChartDataView.as_view(), name='chart_data'),
]