from django.db import models
from django.contrib.auth import get_user_model
from apps.produits.models import Produit

User = get_user_model()


class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('ENTREE', 'Entrée'),
        ('SORTIE', 'Sortie'),
        ('AJUSTEMENT', 'Ajustement'),
        ('INVENTAIRE', 'Inventaire'),
    ]
    
    SOURCE_CHOICES = [
        ('achat', 'Achat'),
        ('vente', 'Vente'),
        ('ajustement', 'Ajustement manuel'),
        ('inventaire', 'Inventaire'),
        ('retour', 'Retour'),
        ('perte', 'Perte'),
    ]
    
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='mouvements')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantite = models.IntegerField()
    quantite_avant = models.PositiveIntegerField()
    quantite_apres = models.PositiveIntegerField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    reference = models.CharField(max_length=100, blank=True, help_text="Référence du document source")
    motif = models.TextField(blank=True)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.produit.nom} ({self.quantite})"
    
    @classmethod
    def create_mouvement(cls, produit, quantite, source, user=None, reference="", motif=""):
        """Create a stock movement and update product stock."""
        quantite_avant = produit.quantite_stock
        
        # Determine movement type
        if quantite > 0:
            type_mouvement = 'ENTREE'
        elif quantite < 0:
            type_mouvement = 'SORTIE'
        else:
            type_mouvement = 'AJUSTEMENT'
        
        # Update product stock
        nouvelle_quantite = quantite_avant + quantite
        if nouvelle_quantite < 0:
            raise ValueError("Stock ne peut pas être négatif")
        
        produit.quantite_stock = nouvelle_quantite
        produit.save(update_fields=['quantite_stock'])
        
        # Create movement record
        mouvement = cls.objects.create(
            produit=produit,
            type=type_mouvement,
            quantite=abs(quantite),
            quantite_avant=quantite_avant,
            quantite_apres=nouvelle_quantite,
            source=source,
            reference=reference,
            motif=motif,
            utilisateur=user
        )
        
        return mouvement


class Inventaire(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_cloture = models.DateTimeField(null=True, blank=True)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    clos = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Inventaire"
        verbose_name_plural = "Inventaires"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom} - {self.date_creation.strftime('%d/%m/%Y')}"
    
    def cloturer(self):
        """Close inventory and create adjustment movements."""
        if self.clos:
            raise ValueError("Inventaire déjà clos")
        
        from django.utils import timezone
        
        for item in self.items.all():
            ecart = item.quantite_comptee - item.quantite_systeme
            if ecart != 0:
                MouvementStock.create_mouvement(
                    produit=item.produit,
                    quantite=ecart,
                    source='inventaire',
                    user=self.utilisateur,
                    reference=f"INV-{self.pk}",
                    motif=f"Ajustement inventaire: {item.produit.nom}"
                )
        
        self.clos = True
        self.date_cloture = timezone.now()
        self.save()


class InventaireItem(models.Model):
    inventaire = models.ForeignKey(Inventaire, on_delete=models.CASCADE, related_name='items')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite_systeme = models.PositiveIntegerField()
    quantite_comptee = models.PositiveIntegerField(default=0)
    note = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Item d'inventaire"
        verbose_name_plural = "Items d'inventaire"
        unique_together = ['inventaire', 'produit']
    
    def __str__(self):
        return f"{self.inventaire.nom} - {self.produit.nom}"
    
    @property
    def ecart(self):
        return self.quantite_comptee - self.quantite_systeme