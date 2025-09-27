from django.contrib import admin
from .models import Categorie, Produit


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'date_creation')
    search_fields = ('nom',)
    prepopulated_fields = {'slug': ('nom',)} if hasattr(Categorie, 'slug') else {}


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'prix_vente', 'quantite_stock', 'stock_critique', 'actif')
    list_filter = ('categorie', 'actif', 'date_ajout')
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}
    list_editable = ('prix_vente', 'quantite_stock', 'actif')
    readonly_fields = ('date_ajout',)
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('nom', 'slug', 'categorie', 'description', 'image')
        }),
        ('Prix', {
            'fields': ('prix_achat', 'prix_vente')
        }),
        ('Stock', {
            'fields': ('quantite_stock', 'seuil_alerte')
        }),
        ('Statut', {
            'fields': ('actif',)
        }),
    )
    
    def stock_critique(self, obj):
        return obj.stock_critique
    stock_critique.boolean = True
    stock_critique.short_description = "Stock critique"