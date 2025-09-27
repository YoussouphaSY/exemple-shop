from django.contrib import admin
from .models import Transaction, Budget, CaisseFonds


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('description', 'type', 'montant', 'categorie', 'date', 'utilisateur', 'budget')
    list_filter = ('type', 'categorie', 'date', 'utilisateur')
    search_fields = ('description',)
    readonly_fields = ('date',)
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Transaction', {
            'fields': ('type', 'montant', 'categorie', 'description')
        }),
        ('Dates', {
            'fields': ('date', 'date_valeur')
        }),
        ('Relations', {
            'fields': ('utilisateur', 'vente', 'achat', 'budget')  # <-- Ajout de budget ici
        }),
        ('Documents', {
            'fields': ('piece_jointe',)
        }),
    )


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('nom', 'montant_prevu', 'montant_realise', 'ecart', 'periode_debut', 'periode_fin', 'actif')
    list_filter = ('actif', 'date_creation')
    search_fields = ('nom', 'description')
    readonly_fields = ('montant_realise', 'ecart', 'pourcentage_realise', 'date_creation')


@admin.register(CaisseFonds)
class CaisseFondsAdmin(admin.ModelAdmin):
    list_display = ('type', 'montant', 'montant_apres', 'date', 'utilisateur')
    list_filter = ('type', 'date')
    readonly_fields = ('date', 'montant_avant', 'montant_apres')