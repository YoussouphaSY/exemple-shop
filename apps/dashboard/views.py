from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
import json

from apps.produits.models import Produit
from apps.ventes.models import Vente, VenteItem
from apps.achats.models import Achat
from apps.stock.models import MouvementStock
from apps.finance.models import Transaction

today = timezone.now().date()
start_week = today - timedelta(days=today.weekday())


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dates for calculations
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        debut_mois = today.replace(day=1)
        debut_semaine = today - timedelta(days=today.weekday())
        
        # Sales statistics
        ventes_aujourd_hui = Vente.objects.filter(date_vente__date=today)
        context['ventes_aujourd_hui'] = ventes_aujourd_hui.count()
        context['ca_aujourd_hui'] = ventes_aujourd_hui.aggregate(
            total=Sum('total_ttc')
        )['total'] or 0
        
        ventes_hier = Vente.objects.filter(date_vente__date=yesterday)
        ca_hier = ventes_hier.aggregate(total=Sum('total_ttc'))['total'] or 0
        
        # Calculate growth percentage
        context['croissance_ca'] = 0
        if ca_hier > 0:
            context['croissance_ca'] = ((context['ca_aujourd_hui'] - ca_hier) / ca_hier) * 100
        
        # Monthly statistics
        context['ca_mois'] = Vente.objects.filter(
            date_vente__date__gte=debut_mois
        ).aggregate(total=Sum('total_ttc'))['total'] or 0
        
        context['ventes_mois'] = Vente.objects.filter(
            date_vente__date__gte=debut_mois
        ).count()
        
        # Stock statistics
        context['stock_total'] = Produit.objects.aggregate(
            total=Sum('quantite_stock')
        )['total'] or 0
        
        context['stock_critique'] = Produit.objects.filter(
            quantite_stock__lte=F('seuil_alerte')
        ).count()
        
        # Financial statistics
        context['solde_total'] = Transaction.get_solde()
        
        # Top products
        context['top_produits'] = VenteItem.objects.filter(
            vente__date_vente__date__gte=debut_mois
        ).values(
            'produit__nom'
        ).annotate(
            total_vendu=Sum('quantite'),
            ca=Sum('total_ttc')
        ).order_by('-total_vendu')[:5]
        
        # Recent activities
        context['ventes_recentes'] = Vente.objects.select_related('vendeur')[:5]
        context['achats_recents'] = Achat.objects.select_related('fournisseur')[:5]
        context['mouvements_recents'] = MouvementStock.objects.select_related(
            'produit', 'utilisateur'
        )[:5]
        
        # Weekly sales chart data (last 7 days)
        ventes_semaine = []
        for i in range(7):
            date = today - timedelta(days=6-i)
            ca_jour = Vente.objects.filter(date_vente__date=date).aggregate(
                total=Sum('total_ttc')
            )['total'] or 0
            ventes_semaine.append({
                'date': date.strftime('%d/%m'),
                'ca': float(ca_jour)
            })
        
        context['ventes_semaine_json'] = json.dumps(ventes_semaine)
        
        # Sales by category
        ventes_par_categorie = VenteItem.objects.filter(
            vente__date_vente__date__gte=debut_mois
        ).values(
            'produit__categorie__nom'
        ).annotate(
            total=Sum('total_ttc')
        ).order_by('-total')
        
        context['ventes_par_categorie_json'] = json.dumps([
            {
                'categorie': item['produit__categorie__nom'] or 'Sans catégorie',
                'total': float(item['total'])
            }
            for item in ventes_par_categorie
        ])
        
        # Financial evolution (last 7 days)
        # Optimized financial evolution
        recettes_data = Transaction.objects.filter(
            type='RECETTE',
            date_valeur__range=[start_week, today]
        ).values('date_valeur').annotate(
            total=Sum('montant')
        )
        
        depenses_data = Transaction.objects.filter(
            type='DEPENSE',
            date_valeur__range=[start_week, today]
        ).values('date_valeur').annotate(
            total=Sum('montant')
        )
                
        recettes_dict = {item['date_valeur'].strftime('%d/%m'): float(item['total'] or 0) for item in recettes_data}
        depenses_dict = {item['date_valeur'].strftime('%d/%m'): float(item['total'] or 0) for item in depenses_data}


                
        finance_evolution = []
        for i in range(7):
            date = today - timedelta(days=6-i)
            date_str = date.strftime('%d/%m')
            finance_evolution.append({
                'date': date_str,
                'recettes': recettes_dict.get(date_str, 0),
                'depenses': depenses_dict.get(date_str, 0)
            })

        context['finance_evolution_json'] = json.dumps(finance_evolution)

        # Calculate stock value
        valeur_stock = 0
        for p in Produit.objects.filter(actif=True):
            if p.prix_vente and p.quantite_stock:
                valeur_stock += float(p.prix_vente) * p.quantite_stock
        context['valeur_stock'] = valeur_stock
        
        return context


class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Date range for analysis
        today = timezone.now().date()
        debut_mois = today.replace(day=1)
        debut_annee = today.replace(month=1, day=1)
        
        # Monthly performance
        mois_data = []
        for i in range(12):
            date = debut_annee.replace(month=i+1) if i < today.month else None
            if date:
                ca = Vente.objects.filter(
                    date_vente__year=today.year,
                    date_vente__month=i+1
                ).aggregate(total=Sum('total_ttc'))['total'] or 0
                
                mois_data.append({
                    'mois': date.strftime('%b'),
                    'ca': float(ca)
                })
        
        context['performance_mensuelle_json'] = json.dumps(mois_data)
        
        # Product performance
        produits_performance = VenteItem.objects.filter(
            vente__date_vente__date__gte=debut_mois
        ).values(
            'produit__nom'
        ).annotate(
            quantite=Sum('quantite'),
            ca=Sum('total_ttc'),
            nb_ventes=Count('vente', distinct=True)
        ).order_by('-ca')[:10]
        
        context['produits_performance'] = list(produits_performance)
        
        # Sales statistics
        context['stats_ventes'] = {
            'ca_moyen': VenteItem.objects.filter(
                vente__date_vente__date__gte=debut_mois
            ).aggregate(avg=Avg('total_ttc'))['avg'] or 0,
            'panier_moyen': Vente.objects.filter(
                date_vente__date__gte=debut_mois
            ).aggregate(avg=Avg('total_ttc'))['avg'] or 0,
        }

        # ⚡ Ajouter max_ca pour le template
        if produits_performance:
            context['max_ca'] = max(p['ca'] for p in produits_performance)
        else:
            context['max_ca'] = 0
        
        return context


class ChartDataView(LoginRequiredMixin, View):
    def get(self, request):
        chart_type = request.GET.get('type', 'sales')
        period = request.GET.get('period', '7')  # days
        
        today = timezone.now().date()
        start_date = today - timedelta(days=int(period))
        
        if chart_type == 'sales':
            data = self.get_sales_chart_data(start_date, today)
        elif chart_type == 'products':
            data = self.get_products_chart_data(start_date, today)
        elif chart_type == 'categories':
            data = self.get_categories_chart_data(start_date, today)
        else:
            data = {}
        
        return JsonResponse(data)
    
    def get_sales_chart_data(self, start_date, end_date):
        """Get daily sales data for chart."""
        data = []
        current_date = start_date
        
        while current_date <= end_date:
            ca = Vente.objects.filter(date_vente__date=current_date).aggregate(
                total=Sum('total_ttc')
            )['total'] or 0
            
            data.append({
                'date': current_date.strftime('%d/%m'),
                'ca': float(ca)
            })
            
            current_date += timedelta(days=1)
        
        return {'sales': data}
    
    def get_products_chart_data(self, start_date, end_date):
        """Get top products data for chart."""
        produits = VenteItem.objects.filter(
            vente__date_vente__date__range=[start_date, end_date]
        ).values(
            'produit__nom'
        ).annotate(
            quantite=Sum('quantite')
        ).order_by('-quantite')[:10]
        
        return {
            'products': [
                {
                    'name': p['produit__nom'],
                    'quantity': p['quantite']
                }
                for p in produits
            ]
        }
    
    def get_categories_chart_data(self, start_date, end_date):
        """Get sales by category data for chart."""
        categories = VenteItem.objects.filter(
            vente__date_vente__date__range=[start_date, end_date]
        ).values(
            'produit__categorie__nom'
        ).annotate(
            total=Sum('total_ttc')
        ).order_by('-total')
        
        return {
            'categories': [
                {
                    'name': c['produit__categorie__nom'] or 'Sans catégorie',
                    'total': float(c['total'])
                }
                for c in categories
            ]
        }