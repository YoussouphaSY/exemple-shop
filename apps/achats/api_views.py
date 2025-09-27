from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Achat, Fournisseur
from .serializers import AchatSerializer, FournisseurSerializer


class AchatViewSet(viewsets.ModelViewSet):
    queryset = Achat.objects.all()
    serializer_class = AchatSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['statut', 'fournisseur']
    ordering_fields = ['date_achat', 'total_ttc']
    ordering = ['-date_achat']


class FournisseurViewSet(viewsets.ModelViewSet):
    queryset = Fournisseur.objects.filter(actif=True)
    serializer_class = FournisseurSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'contact']
    ordering = ['nom']