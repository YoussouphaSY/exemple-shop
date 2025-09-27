from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta

from apps.produits.models import Produit
from apps.ventes.models import Vente, VenteItem
from apps.achats.models import Achat
from apps.finance.models import Transaction


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        today = timezone.now().date()
        debut_mois = today.replace(day=1)
        
        # Core statistics
        stats = {
            'ventes_aujourd_hui': Vente.objects.filter(date_vente__date=today).count(),
            'ca_aujourd_hui': Vente.objects.filter(date_vente__date=today).aggregate(
                total=Sum('total_ttc')
            )['total'] or 0,
            'ca_mois': Vente.objects.filter(date_vente__date__gte=debut_mois).aggregate(
                total=Sum('total_ttc')
            )['total'] or 0,
            'stock_critique': Produit.objects.filter(
                quantite_stock__lte=F('seuil_alerte')
            ).count(),
            'solde_total': Transaction.get_solde(),
            'nb_produits': Produit.objects.filter(actif=True).count(),
            'nb_commandes_en_attente': Achat.objects.filter(statut='commande').count(),
        }
        
        return Response(stats)


class ChartDataView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        chart_type = request.GET.get('type', 'sales')
        period = int(request.GET.get('period', '30'))
        
        today = timezone.now().date()
        start_date = today - timedelta(days=period)
        
        if chart_type == 'sales_evolution':
            data = self.get_sales_evolution(start_date, today)
        elif chart_type == 'top_products':
            data = self.get_top_products(start_date, today)
        elif chart_type == 'category_distribution':
            data = self.get_category_distribution(start_date, today)
        elif chart_type == 'financial_overview':
            data = self.get_financial_overview(start_date, today)
        else:
            data = {}
        
        return Response(data)
    
    def get_sales_evolution(self, start_date, end_date):
        """Sales evolution over time."""
        data = []
        current_date = start_date
        
        while current_date <= end_date:
            ca = Vente.objects.filter(date_vente__date=current_date).aggregate(
                total=Sum('total_ttc')
            )['total'] or 0
            
            nb_ventes = Vente.objects.filter(date_vente__date=current_date).count()
            
            data.append({
                'date': current_date.isoformat(),
                'ca': float(ca),
                'nb_ventes': nb_ventes
            })
            
            current_date += timedelta(days=1)
        
        return data
    
    def get_top_products(self, start_date, end_date):
        """Top selling products."""
        return list(VenteItem.objects.filter(
            vente__date_vente__date__range=[start_date, end_date]
        ).values(
            'produit__nom'
        ).annotate(
            quantite_vendue=Sum('quantite'),
            ca=Sum('total_ttc')
        ).order_by('-quantite_vendue')[:10])
    
    def get_category_distribution(self, start_date, end_date):
        """Sales distribution by category."""
        return list(VenteItem.objects.filter(
            vente__date_vente__date__range=[start_date, end_date]
        ).values(
            'produit__categorie__nom'
        ).annotate(
            total=Sum('total_ttc'),
            quantite=Sum('quantite')
        ).order_by('-total'))
    
    def get_financial_overview(self, start_date, end_date):
        """Financial overview for the period."""
        recettes = Transaction.objects.filter(
            type='RECETTE',
            date_valeur__range=[start_date, end_date]
        ).aggregate(total=Sum('montant'))['total'] or 0
        
        depenses = Transaction.objects.filter(
            type='DEPENSE',
            date_valeur__range=[start_date, end_date]
        ).aggregate(total=Sum('montant'))['total'] or 0
        
        return {
            'recettes': float(recettes),
            'depenses': float(depenses),
            'benefice': float(recettes - depenses),
            'marge': float((recettes - depenses) / recettes * 100) if recettes > 0 else 0
        }