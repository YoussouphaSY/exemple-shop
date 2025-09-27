from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'ventes', api_views.VenteViewSet)

urlpatterns = router.urls