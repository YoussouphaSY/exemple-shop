from django.contrib import admin
from .models import MouvementStock, Inventaire, InventaireItem


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('produit', 'type', 'quantite', 'source', 'utilisateur', 'date')
    list_filter = ('type', 'source', 'date')
    search_fields = ('produit__nom', 'reference')
    readonly_fields = ('date',)
    
    def has_add_permission(self, request):
        return False  # Prevent direct creation, use through other models


class InventaireItemInline(admin.TabularInline):
    model = InventaireItem
    extra = 0
    readonly_fields = ('quantite_systeme',)


@admin.register(Inventaire)
class InventaireAdmin(admin.ModelAdmin):
    list_display = ('nom', 'utilisateur', 'date_creation', 'clos')
    list_filter = ('clos', 'date_creation')
    search_fields = ('nom', 'description')
    inlines = [InventaireItemInline]
    readonly_fields = ('date_creation', 'date_cloture')