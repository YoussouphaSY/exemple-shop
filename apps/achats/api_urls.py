from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'achats', api_views.AchatViewSet)
router.register(r'fournisseurs', api_views.FournisseurViewSet)

urlpatterns = router.urls