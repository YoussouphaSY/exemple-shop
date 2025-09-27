from django.contrib import admin
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from django.urls import path
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import json

from apps.produits.models import Produit, Categorie
from apps.ventes.models import Vente, VenteItem
from apps.achats.models import Achat, Fournisseur
from apps.finance.models import Transaction
from apps.stock.models import MouvementStock
from apps.users.models import UserSession, DailyAttendance

User = get_user_model()


class Shop360AdminSite(AdminSite):
    site_header = "🇸🇳 Shop360 Administration"
    site_title = "Shop360 Admin"
    index_title = "Tableau de Bord Administrateur"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('notifications/', self.admin_view(self.notifications_view), name='notifications'),
            path('attendance/', self.admin_view(self.attendance_view), name='attendance'),
            path('online-users/', self.admin_view(self.online_users_view), name='online_users'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """Vue dashboard personnalisée pour l'admin."""
        today = timezone.now().date()
        debut_mois = today.replace(day=1)
        debut_semaine = today - timedelta(days=today.weekday())
        
        # Statistiques générales
        stats = {
            'total_produits': Produit.objects.filter(actif=True).count(),
            'total_categories': Categorie.objects.count(),
            'total_fournisseurs': Fournisseur.objects.filter(actif=True).count(),
            'total_users': User.objects.filter(is_active=True).count(),
            
            # Ventes
            'ventes_aujourd_hui': Vente.objects.filter(date_vente__date=today).count(),
            'ca_aujourd_hui': Vente.objects.filter(date_vente__date=today).aggregate(
                total=Sum('total_ttc')
            )['total'] or 0,
            'ca_semaine': Vente.objects.filter(date_vente__date__gte=debut_semaine).aggregate(
                total=Sum('total_ttc')
            )['total'] or 0,
            'ca_mois': Vente.objects.filter(date_vente__date__gte=debut_mois).aggregate(
                total=Sum('total_ttc')
            )['total'] or 0,
            
            # Stock
            'stock_critique': Produit.objects.filter(
                quantite_stock__lte=F('seuil_alerte')
            ).count(),
            'valeur_stock': sum(
                p.prix_achat * p.quantite_stock 
                for p in Produit.objects.filter(actif=True)
            ),
            
            # Finance
            'solde_total': Transaction.get_solde(),
            'transactions_mois': Transaction.objects.filter(
                date__date__gte=debut_mois
            ).count(),
            
            # Utilisateurs connectés
            'users_online': UserSession.objects.filter(
                is_active=True,
                login_time__gte=today
            ).count(),
        }
        
        # Top produits
        top_produits = VenteItem.objects.filter(
            vente__date_vente__date__gte=debut_mois
        ).values('produit__nom').annotate(
            total_vendu=Sum('quantite'),
            ca=Sum('total_ttc')
        ).order_by('-total_vendu')[:5]
        
        # Évolution des ventes (7 derniers jours)
        ventes_evolution = []
        for i in range(7):
            date = today - timedelta(days=6-i)
            ca = Vente.objects.filter(date_vente__date=date).aggregate(
                total=Sum('total_ttc')
            )['total'] or 0
            ventes_evolution.append({
                'date': date.strftime('%d/%m'),
                'ca': float(ca)
            })
        
        # Évolution financière (recettes vs dépenses)
        finance_evolution = []
        for i in range(7):
            date = today - timedelta(days=6-i)
            recettes = Transaction.objects.filter(
                type='RECETTE', date_valeur=date
            ).aggregate(total=Sum('montant'))['total'] or 0
            depenses = Transaction.objects.filter(
                type='DEPENSE', date_valeur=date
            ).aggregate(total=Sum('montant'))['total'] or 0
            finance_evolution.append({
                'date': date.strftime('%d/%m'),
                'recettes': float(recettes),
                'depenses': float(depenses)
            })
        
        # Alertes et notifications
        alertes = []
        
        # Stock critique
        produits_critiques = Produit.objects.filter(
            quantite_stock__lte=F('seuil_alerte')
        )[:5]
        
        for produit in produits_critiques:
            alertes.append({
                'type': 'warning',
                'message': f"Stock critique: {produit.nom} ({produit.quantite_stock} restants)",
                'url': f"/produits/{produit.slug}/",
                'date': timezone.now()
            })
        
        # Achats en attente
        achats_attente = Achat.objects.filter(statut='commande').count()
        if achats_attente > 0:
            alertes.append({
                'type': 'info',
                'message': f"{achats_attente} achat(s) en attente de réception",
                'url': "/achats/?statut=commande",
                'date': timezone.now()
            })
        
        # Utilisateurs connectés aujourd'hui
        users_today = UserSession.objects.filter(
            login_time__date=today,
            is_active=True
        ).select_related('user')
        
        context = {
            'stats': stats,
            'top_produits': top_produits,
            'ventes_evolution': json.dumps(ventes_evolution),
            'finance_evolution': json.dumps(finance_evolution),
            'alertes': alertes,
            'produits_critiques': produits_critiques,
            'users_online': users_today,
        }
        
        return TemplateResponse(request, 'admin/dashboard.html', context)
    
    def notifications_view(self, request):
        """Vue des notifications pour l'admin."""
        from apps.dashboard.models import Notification
        
        notifications = Notification.objects.filter(
            utilisateur=request.user
        ).order_by('-date_creation')[:50]
        
        context = {
            'notifications': notifications
        }
        
        return TemplateResponse(request, 'admin/notifications.html', context)
    
    def attendance_view(self, request):
        """Vue de présence des utilisateurs."""
        today = timezone.now().date()
        date_filter = request.GET.get('date', str(today))
        
        if isinstance(date_filter, str):
            from datetime import datetime
            date_filter = datetime.strptime(date_filter, '%Y-%m-%d').date()
        
        # Présences du jour
        attendances = DailyAttendance.objects.filter(
            date=date_filter
        ).select_related('user').order_by('user__username')
        
        # Sessions actives
        active_sessions = UserSession.objects.filter(
            is_active=True,
            login_time__date=date_filter
        ).select_related('user')
        
        # Get active users for template
        active_users = [session.user for session in active_sessions]
        
        context = {
            'attendances': attendances,
            'active_sessions': active_sessions,
            'selected_date': date_filter,
            'active_users': active_users,
        }
        
        return TemplateResponse(request, 'admin/attendance.html', context)
    
    def online_users_view(self, request):
        """Vue des utilisateurs connectés."""
        online_sessions = UserSession.objects.filter(
            is_active=True
        ).select_related('user').order_by('-login_time')
        
        context = {
            'online_sessions': online_sessions
        }
        
        return TemplateResponse(request, 'admin/online_users.html', context)
    
    def index(self, request, extra_context=None):
        """Override de la page d'accueil admin."""
        return self.dashboard_view(request)


# Remplacer le site admin par défaut
admin_site = Shop360AdminSite(name='shop360_admin')

# Enregistrer tous les modèles
from apps.produits.admin import ProduitAdmin, CategorieAdmin
from apps.ventes.admin import VenteAdmin
from apps.achats.admin import AchatAdmin, FournisseurAdmin
from apps.finance.admin import TransactionAdmin, BudgetAdmin, CaisseFondsAdmin
from apps.stock.admin import MouvementStockAdmin, InventaireAdmin
from apps.users.admin import UserAdmin, UserSessionAdmin, DailyAttendanceAdmin
from apps.dashboard.models import Notification, ParametreSysteme

admin_site.register(Produit, ProduitAdmin)
admin_site.register(Categorie, CategorieAdmin)
admin_site.register(Vente, VenteAdmin)
admin_site.register(Achat, AchatAdmin)
admin_site.register(Fournisseur, FournisseurAdmin)
admin_site.register(Transaction, TransactionAdmin)
admin_site.register(MouvementStock, MouvementStockAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(UserSession, UserSessionAdmin)
admin_site.register(DailyAttendance, DailyAttendanceAdmin)

# Enregistrer les modèles manquants
from apps.stock.models import Inventaire, InventaireItem
from apps.finance.models import Budget, CaisseFonds

admin_site.register(Inventaire, InventaireAdmin)
admin_site.register(Budget, BudgetAdmin)
admin_site.register(CaisseFonds, CaisseFondsAdmin)
admin_site.register(Notification)
admin_site.register(ParametreSysteme)