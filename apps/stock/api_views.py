from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import MouvementStock, Inventaire
from .serializers import MouvementStockSerializer, InventaireSerializer


class MouvementStockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MouvementStock.objects.all()
    serializer_class = MouvementStockSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['type', 'source', 'produit']
    ordering_fields = ['date']
    ordering = ['-date']


class InventaireViewSet(viewsets.ModelViewSet):
    queryset = Inventaire.objects.all()
    serializer_class = InventaireSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['clos']
    ordering = ['-date_creation']