from django.urls import path
from . import api_views

urlpatterns = [
    path('stats/', api_views.DashboardStatsView.as_view(), name='dashboard_stats'),
    path('charts/', api_views.ChartDataView.as_view(), name='chart_data'),
]