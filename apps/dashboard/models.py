from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Succès'),
        ('warning', 'Avertissement'),
        ('danger', 'Erreur'),
    ]
    
    titre = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    url = models.URLField(blank=True, help_text="URL vers l'élément concerné")
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.get_type_display()}"


class ParametreSysteme(models.Model):
    """Paramètres globaux du système."""
    nom_boutique = models.CharField(max_length=200, default="Shop360")
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    devise = models.CharField(max_length=10, default="FCFA")
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    seuil_stock_global = models.PositiveIntegerField(default=5)
    
    class Meta:
        verbose_name = "Paramètre système"
        verbose_name_plural = "Paramètres système"
    
    def __str__(self):
        return self.nom_boutique