from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import Transaction, Budget, CaisseFonds
from .serializers import TransactionSerializer, BudgetSerializer, CaisseFondsSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['type', 'categorie']
    ordering_fields = ['date', 'montant']
    ordering = ['-date']
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Get financial statistics."""
        stats = {
            'solde': Transaction.get_solde(),
            'total_recettes': Transaction.objects.filter(type='RECETTE').aggregate(
                total=Sum('montant')
            )['total'] or 0,
            'total_depenses': Transaction.objects.filter(type='DEPENSE').aggregate(
                total=Sum('montant')
            )['total'] or 0,
            'solde_caisse': CaisseFonds.get_solde_caisse(),
        }
        
        return Response(stats)


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['actif']
    ordering = ['-date_creation']