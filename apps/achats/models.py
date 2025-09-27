from django.db import models
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.produits.models import Produit
from apps.stock.models import MouvementStock
from apps.finance.models import Transaction

User = get_user_model()


class Fournisseur(models.Model):
    nom = models.CharField(max_length=200)
    contact = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Achat(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('commande', 'Commandé'),
        ('recu', 'Reçu'),
        ('facture', 'Facturé'),
    ]
    
    numero = models.CharField(max_length=20, unique=True, blank=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name='achats')
    date_achat = models.DateTimeField(auto_now_add=True)
    date_livraison = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Achat"
        verbose_name_plural = "Achats"
        ordering = ['-date_achat']
    
    def __str__(self):
        return f"Achat {self.numero} - {self.fournisseur.nom}"
    
    def save(self, *args, **kwargs):
        if not self.numero:
            # Generate purchase number
            from django.utils import timezone
            today = timezone.now()
            prefix = f"A{today.strftime('%Y%m%d')}"
            last_purchase = Achat.objects.filter(numero__startswith=prefix).order_by('-numero').first()
            if last_purchase:
                last_num = int(last_purchase.numero[-4:])
                new_num = last_num + 1
            else:
                new_num = 1
            self.numero = f"{prefix}{new_num:04d}"
        
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate total amounts from purchase items."""
        items = self.items.all()
        total_ht = sum(item.total_ht for item in items)
        total_ttc = sum(item.total_ttc for item in items)
        
        self.total_ht = total_ht
        self.total_ttc = total_ttc
        self.save(update_fields=['total_ht', 'total_ttc'])
    
    def recevoir(self):
        """Mark as received and update stock."""
        if self.statut != 'commande':
            raise ValueError("Seuls les achats commandés peuvent être reçus")
        
        with transaction.atomic():
            # Update stock for each item
            for item in self.items.all():
                MouvementStock.create_mouvement(
                    produit=item.produit,
                    quantite=item.quantite_recue or item.quantite,
                    source='achat',
                    user=self.utilisateur,
                    reference=self.numero
                )
                
                # Update product purchase price
                item.produit.prix_achat = item.prix_unitaire
                item.produit.save(update_fields=['prix_achat'])
            
            self.statut = 'recu'
            self.save(update_fields=['statut'])
    
    def facturer(self):
        """Mark as invoiced and create expense transaction."""
        if self.statut != 'recu':
            raise ValueError("Seuls les achats reçus peuvent être facturés")
        
        with transaction.atomic():
            # Create financial transaction
            Transaction.objects.create(
                type='DEPENSE',
                montant=self.total_ttc,
                description=f"Achat {self.numero} - {self.fournisseur.nom}",
                achat=self,
                utilisateur=self.utilisateur
            )
            
            self.statut = 'facture'
            self.save(update_fields=['statut'])


class AchatItem(models.Model):
    achat = models.ForeignKey(Achat, on_delete=models.CASCADE, related_name='items')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    quantite_recue = models.PositiveIntegerField(null=True, blank=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Article acheté"
        verbose_name_plural = "Articles achetés"
        unique_together = ['achat', 'produit']
    
    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"
    
    def save(self, *args, **kwargs):
        # Calculate totals (assuming no VAT for simplicity)
        self.total_ht = self.quantite * self.prix_unitaire
        self.total_ttc = self.total_ht
        
        super().save(*args, **kwargs)
        
        # Update purchase totals
        if self.achat_id:
            self.achat.calculate_totals()