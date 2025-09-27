from django.contrib import admin
from .models import Fournisseur, Achat, AchatItem


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'contact', 'telephone', 'email', 'actif')
    list_filter = ('actif', 'date_creation')
    search_fields = ('nom', 'contact', 'email')


class AchatItemInline(admin.TabularInline):
    model = AchatItem
    extra = 1
    fields = ['produit', 'quantite', 'quantite_recue', 'prix_unitaire', 'total_ttc']
    readonly_fields = ['total_ttc']


@admin.register(Achat)
class AchatAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fournisseur', 'statut', 'total_ttc', 'date_achat')
    list_filter = ('statut', 'date_achat', 'fournisseur')
    search_fields = ('numero', 'fournisseur__nom')
    readonly_fields = ('numero', 'total_ht', 'total_ttc', 'date_achat')
    inlines = [AchatItemInline]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('numero', 'fournisseur', 'date_achat', 'date_livraison')
        }),
        ('Statut', {
            'fields': ('statut', 'utilisateur')
        }),
        ('Totaux', {
            'fields': ('total_ht', 'total_ttc')
        }),
        ('Notes', {
            'fields': ('note',)
        }),
    )