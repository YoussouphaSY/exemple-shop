from django.contrib import admin
from .models import Vente, VenteItem


class VenteItemInline(admin.TabularInline):
    model = VenteItem
    extra = 1
    fields = ['produit', 'quantite', 'prix_unitaire', 'total_ttc']
    readonly_fields = ['total_ttc']


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('numero', 'client', 'total_ttc', 'mode_paiement', 'vendeur', 'date_vente')
    list_filter = ('mode_paiement', 'date_vente', 'vendeur')
    search_fields = ('numero', 'client', 'telephone_client')
    readonly_fields = ('numero', 'total_ht', 'total_ttc', 'date_vente')
    inlines = [VenteItemInline]
    
    fieldsets = (
        ('Informations client', {
            'fields': ('client', 'telephone_client')
        }),
        ('Détails vente', {
            'fields': ('numero', 'mode_paiement', 'vendeur', 'date_vente')
        }),
        ('Totaux', {
            'fields': ('total_ht', 'total_ttc')
        }),
        ('Notes', {
            'fields': ('note',)
        }),
    )