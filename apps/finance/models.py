from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum
from decimal import Decimal
from django.db.models import Q
User = get_user_model()


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('RECETTE', 'Recette'),
        ('DEPENSE', 'Dépense'),
    ]
    
    CATEGORY_CHOICES = [
        ('vente', 'Vente'),
        ('achat', 'Achat fournisseur'),
        ('frais', 'Frais généraux'),
        ('salaire', 'Salaire'),
        ('loyer', 'Loyer'),
        ('electricite', 'Électricité'),
        ('telephone', 'Téléphone/Internet'),
        ('transport', 'Transport'),
        ('publicite', 'Publicité'),
        ('autre', 'Autre'),
    ]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    budget = models.ForeignKey('finance.Budget', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    categorie = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='autre')
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    date_valeur = models.DateField(null=True, blank=True, help_text="Date de valeur de la transaction")
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Relations optionnelles vers ventes/achats
    vente = models.ForeignKey('ventes.Vente', on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')
    achat = models.ForeignKey('achats.Achat', on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')
    
    # Pièce justificative
    piece_jointe = models.FileField(upload_to='justificatifs/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.montant}€ - {self.description[:50]}"
    
    def save(self, *args, **kwargs):
        # Set date_valeur to today if not provided
        if not self.date_valeur:
            from django.utils import timezone
            self.date_valeur = timezone.now().date()
        
        # Set category based on linked objects
        if self.vente:
            self.categorie = 'vente'
        elif self.achat:
            self.categorie = 'achat'
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solde(cls):
        """Calculate current balance."""
        recettes = cls.objects.filter(type='RECETTE').aggregate(
            total=Sum('montant')
        )['total'] or Decimal('0')
        
        depenses = cls.objects.filter(type='DEPENSE').aggregate(
            total=Sum('montant')
        )['total'] or Decimal('0')
        
        return recettes - depenses
    
    @classmethod
    def get_ca_periode(cls, date_debut, date_fin):
        """Get revenue for a period."""
        return cls.objects.filter(
            type='RECETTE',
            date_valeur__range=[date_debut, date_fin]
        ).aggregate(total=Sum('montant'))['total'] or Decimal('0')
    
    @classmethod
    def get_depenses_periode(cls, date_debut, date_fin):
        """Get expenses for a period."""
        return cls.objects.filter(
            type='DEPENSE',
            date_valeur__range=[date_debut, date_fin]
        ).aggregate(total=Sum('montant'))['total'] or Decimal('0')



class Budget(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    montant_prevu = models.DecimalField(max_digits=10, decimal_places=2)
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    categories = models.CharField(max_length=200, help_text="Catégories concernées (séparées par des virgules)")
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Budget"
        verbose_name_plural = "Budgets"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom} - {self.montant_prevu}€"
    

    @property
    def montant_realise(self):
        categories_list = [cat.strip().lower() for cat in self.categories.split(',') if cat.strip()]
        
        transactions = Transaction.objects.filter(
            date_valeur__range=[self.periode_debut, self.periode_fin],
            categorie__in=categories_list
        )
        
        # Inclure les recettes et/ou dépenses selon catégorie
        # Par exemple, ici on inclut tout ce qui est dans les catégories listées
        total = transactions.aggregate(total=Sum('montant'))['total'] or Decimal('0')
        return total



    @property
    def ecart(self):
        """Écart entre prévu et réalisé."""
        montant_prevu = self.montant_prevu or Decimal(0)
        montant_realise = self.montant_realise or Decimal(0)
        return montant_prevu - montant_realise
    
    @property
    def pourcentage_realise(self):
        """Pourcentage du budget utilisé."""
        if not self.montant_prevu or self.montant_prevu == 0:
            return 0
        return (self.montant_realise / self.montant_prevu) * 100

# class CaisseFonds(models.Model):
#     """Track cash fund movements."""
    
#     TYPE_CHOICES = [
#         ('ouverture', 'Ouverture caisse'),
#         ('fermeture', 'Fermeture caisse'),
#         ('approvisionnement', 'Approvisionnement'),
#         ('retrait', 'Retrait'),
#     ]
    
#     type = models.CharField(max_length=20, choices=TYPE_CHOICES)
#     montant = models.DecimalField(max_digits=10, decimal_places=2)
#     montant_avant = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     montant_apres = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     date = models.DateTimeField(auto_now_add=True)
#     utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     note = models.TextField(blank=True)

#     def save(self, *args, **kwargs):
#         # Calcul du montant_avant
#         dernier_solde = CaisseFonds.objects.order_by('-date').first()
#         self.montant_avant = dernier_solde.montant_apres if dernier_solde else Decimal('0')
        
#         # Calcul du montant_apres selon le type
#         if self.type in ['ouverture', 'approvisionnement']:
#             self.montant_apres = self.montant_avant + self.montant
#         elif self.type in ['retrait', 'fermeture']:
#             self.montant_apres = self.montant_avant - self.montant
#         else:
#             self.montant_apres = self.montant_avant
        
#         super().save(*args, **kwargs)
    
#     class Meta:
#         verbose_name = "Mouvement caisse"
#         verbose_name_plural = "Mouvements caisse"
#         ordering = ['-date']
    
#     def __str__(self):
#         return f"{self.get_type_display()} - {self.montant}€"
    
#     @classmethod
#     def get_solde_caisse(cls):
#         """Get current cash balance."""
#         mouvements = cls.objects.all().order_by('date')  # ordre croissant
#         print("=== DEBUG SOLDE CAISSE ===")
#         for m in mouvements:
#             print(f"{m.date} | {m.type} | {m.montant} | avant: {m.montant_avant} | après: {m.montant_apres}")
        
#         dernier_mouvement = cls.objects.order_by('-date').first()
#         solde = dernier_mouvement.montant_apres if dernier_mouvement else Decimal('0')
#         print(f"Solde actuel calculé : {solde}")
#         return solde


# class CaisseFonds(models.Model):
#     TYPE_CHOICES = [
#         ('ouverture', 'Ouverture caisse'),
#         ('fermeture', 'Fermeture caisse'),
#         ('approvisionnement', 'Approvisionnement'),
#         ('retrait', 'Retrait'),
#     ]
    
#     type = models.CharField(max_length=20, choices=TYPE_CHOICES)
#     montant = models.DecimalField(max_digits=10, decimal_places=2)
#     montant_avant = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     montant_apres = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     date = models.DateTimeField(auto_now_add=True)
#     utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     note = models.TextField(blank=True)

#     def save(self, *args, **kwargs):
#         # Recalculer uniquement pour ce mouvement
#         dernier_mouvement = CaisseFonds.objects.order_by('-date').first()
#         self.montant_avant = dernier_mouvement.montant_apres if dernier_mouvement else Decimal('0')
        
#         if self.type in ['ouverture', 'approvisionnement']:
#             self.montant_apres = self.montant_avant + self.montant
#         elif self.type in ['retrait', 'fermeture']:
#             self.montant_apres = self.montant_avant - self.montant
#         else:
#             self.montant_apres = self.montant_avant

#         super().save(*args, **kwargs)

#     @classmethod
#     def get_solde_caisse(cls):
#         """Calculer le solde actuel sans toucher à la DB."""
#         dernier_mouvement = cls.objects.order_by('-date').first()
#         return dernier_mouvement.montant_apres if dernier_mouvement else Decimal('0')


class CaisseFonds(models.Model):
    TYPE_CHOICES = [
        ('ouverture', 'Ouverture caisse'),
        ('fermeture', 'Fermeture caisse'),
        ('approvisionnement', 'Approvisionnement'),
        ('retrait', 'Retrait'),
    ]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    montant_avant = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montant_apres = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    note = models.TextField(blank=True)
    categorie_depense = models.CharField(
        max_length=20,
        choices=Transaction.CATEGORY_CHOICES,
        default='autre',
        help_text="Catégorie utilisée pour la Transaction générée"
    )

    def save(self, *args, **kwargs):
        # Calcul du montant_avant
        dernier_mouvement = CaisseFonds.objects.order_by('-date').first()
        self.montant_avant = dernier_mouvement.montant_apres if dernier_mouvement else Decimal('0')
        
        # Calcul du montant_apres
        if self.type in ['ouverture', 'approvisionnement']:
            self.montant_apres = self.montant_avant + self.montant
        elif self.type in ['retrait', 'fermeture']:
            self.montant_apres = self.montant_avant - self.montant
        else:
            self.montant_apres = self.montant_avant

        super().save(*args, **kwargs)

        # Création automatique de la Transaction si c'est un retrait ou une fermeture
        if self.type in ['retrait', 'fermeture'] and self.montant > 0:
            Transaction.objects.create(
                type='DEPENSE',
                montant=self.montant,
                categorie=self.categorie_depense,
                description=f"{self.get_type_display()} caisse: {self.note}",
                date_valeur=self.date.date(),
                utilisateur=self.utilisateur
            )

    @classmethod
    def get_solde_caisse(cls):
        """Calculer le solde actuel sans toucher à la DB."""
        dernier_mouvement = cls.objects.order_by('-date').first()
        return dernier_mouvement.montant_apres if dernier_mouvement else Decimal('0')
