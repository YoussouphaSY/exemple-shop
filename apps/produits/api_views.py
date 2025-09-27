from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from .models import Produit, Categorie
from .serializers import ProduitSerializer, CategorieSerializer


class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.filter(actif=True)
    serializer_class = ProduitSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categorie', 'actif']
    search_fields = ['nom', 'description']
    ordering_fields = ['nom', 'prix_vente', 'quantite_stock', 'date_ajout']
    ordering = ['-date_ajout']
    
    @action(detail=False, methods=['get'])
    def stock_critique(self, request):
        """Get products with critical stock levels."""
        produits = self.queryset.filter(quantite_stock__lte=F('seuil_alerte'))
        serializer = self.get_serializer(produits, many=True)
        return Response(serializer.data)


class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom']
    ordering = ['nom']