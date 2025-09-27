from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'transactions', api_views.TransactionViewSet)
router.register(r'budgets', api_views.BudgetViewSet)

urlpatterns = router.urls