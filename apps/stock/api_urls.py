from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'mouvements', api_views.MouvementStockViewSet)
router.register(r'inventaires', api_views.InventaireViewSet)

urlpatterns = router.urls