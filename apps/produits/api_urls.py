from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'produits', api_views.ProduitViewSet)
router.register(r'categories', api_views.CategorieViewSet)

urlpatterns = router.urls