from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Vente
from .serializers import VenteSerializer


class VenteViewSet(viewsets.ModelViewSet):
    queryset = Vente.objects.all()
    serializer_class = VenteSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['mode_paiement', 'vendeur']
    ordering_fields = ['date_vente', 'total_ttc']
    ordering = ['-date_vente']
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Get sales statistics."""
        from django.utils import timezone
        today = timezone.now().date()
        
        stats = {
            'ventes_aujourd_hui': self.queryset.filter(date_vente__date=today).count(),
            'ca_aujourd_hui': self.queryset.filter(date_vente__date=today).aggregate(
                total=Sum('total_ttc')
            )['total'] or 0,
            'total_ventes': self.queryset.count(),
            'ca_total': self.queryset.aggregate(total=Sum('total_ttc'))['total'] or 0,
        }
        
        return Response(stats)