from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from apps.produits.models import Produit
from apps.stock.models import MouvementStock
from apps.finance.models import Transaction

User = get_user_model()


class Vente(models.Model):
    MODE_PAIEMENT_CHOICES = [
        ('especes', 'Espèces'),
        ('carte', 'Carte bancaire'),
        ('cheque', 'Chèque'),
        ('virement', 'Virement'),
        ('mobile', 'Paiement mobile'),
    ]
    
    numero = models.CharField(max_length=20, unique=True, blank=True)
    client = models.CharField(max_length=200, blank=True)
    telephone_client = models.CharField(max_length=15, blank=True)
    total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, default='especes')
    vendeur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="ventes_vendeur")
    date_vente = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventes_utilisateur'  # <- correspond à user.ventes
    )
    
    class Meta:
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"
        ordering = ['-date_vente']
    
    def __str__(self):
        return f"Vente {self.numero} - {self.total_ttc}€"
    
    def save(self, *args, **kwargs):
        if not self.numero:
            # Generate sale number
            from django.utils import timezone
            today = timezone.now()
            prefix = f"V{today.strftime('%Y%m%d')}"
            last_sale = Vente.objects.filter(numero__startswith=prefix).order_by('-numero').first()
            if last_sale:
                last_num = int(last_sale.numero[-4:])
                new_num = last_num + 1
            else:
                new_num = 1
            self.numero = f"{prefix}{new_num:04d}"
        
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate total amounts from sale items."""
        items = self.items.all()
        total_ht = sum(item.total_ht for item in items)
        total_ttc = sum(item.total_ttc for item in items)
        
        self.total_ht = total_ht
        self.total_ttc = total_ttc
        self.save(update_fields=['total_ht', 'total_ttc'])
    
    def finaliser(self):
        """Finalize sale: update stock and create financial transaction."""
        if not self.items.exists():
            raise ValidationError("Impossible de finaliser une vente sans articles")
        
        with transaction.atomic():
            # Update stock for each item
            for item in self.items.all():
                if item.produit.quantite_stock < item.quantite:
                    raise ValidationError(
                        f"Stock insuffisant pour {item.produit.nom}. "
                        f"Stock disponible: {item.produit.quantite_stock}"
                    )
                
                # Create stock movement
                MouvementStock.create_mouvement(
                    produit=item.produit,
                    quantite=-item.quantite,  # Negative for sale
                    source='vente',
                    user=self.vendeur,
                    reference=self.numero
                )
            
            # Create financial transaction
            Transaction.objects.create(
                type='RECETTE',
                montant=self.total_ttc,
                description=f"Vente {self.numero}",
                vente=self,
                utilisateur=self.vendeur
            )
            
            # Recalculate totals
            self.calculate_totals()


class VenteItem(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='items')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    prix_original = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Prix de vente standard du produit")
    total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Article vendu"
        verbose_name_plural = "Articles vendus"
        unique_together = ['vente', 'produit']
    
    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"
    
    @property
    def reduction_accordee(self):
        """Calcule la réduction accordée par rapport au prix original."""
        if self.prix_original and self.prix_original > self.prix_unitaire:
            return self.prix_original - self.prix_unitaire
        return 0
    
    @property
    def pourcentage_reduction(self):
        """Calcule le pourcentage de réduction accordé."""
        if self.prix_original and self.prix_original > 0:
            return ((self.prix_original - self.prix_unitaire) / self.prix_original) * 100
        return 0
    
    def save(self, *args, **kwargs):
        # Sauvegarder le prix original si non spécifié
        if not self.prix_original:
            self.prix_original = self.produit.prix_vente
        
        # Use product's sale price if not specified
        if not self.prix_unitaire:
            self.prix_unitaire = self.produit.prix_vente
        
        # Calculate totals (assuming no VAT for simplicity)
        self.total_ht = self.quantite * self.prix_unitaire
        self.total_ttc = self.total_ht
        
        super().save(*args, **kwargs)
        
        # Update sale totals
        if self.vente_id:
            self.vente.calculate_totals()
    
    def clean(self):
        if self.quantite > self.produit.quantite_stock:
            raise ValidationError(f"Stock insuffisant. Disponible: {self.produit.quantite_stock}")