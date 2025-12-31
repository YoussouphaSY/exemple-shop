from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from PIL import Image
import os


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Produit(models.Model):
    nom = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')
    description = models.TextField(blank=True)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.PositiveIntegerField(default=0)
    seuil_alerte = models.PositiveIntegerField(default=5, help_text="Quantité minimum avant alerte")
    date_ajout = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-date_ajout']
    
    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        
        # Ensure unique slug
        original_slug = self.slug
        counter = 1
        while Produit.objects.exclude(pk=self.pk).filter(slug=self.slug).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        super().save(*args, **kwargs)
        
        # Resize image if uploaded
        if self.image:
            self.resize_image()
    
    def resize_image(self):
        """Resize uploaded image to max 800x600."""
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 600 or img.width > 800:
                img.thumbnail((800, 600))
                img.save(self.image.path)
    
    def get_absolute_url(self):
        return reverse('produits:detail', kwargs={'pk': self.pk})
    
    def update_stock(self, delta):
        """Update stock quantity. Positive delta for increase, negative for decrease."""
        new_quantity = self.quantite_stock + delta
        if new_quantity < 0:
            raise ValueError("Stock ne peut pas être négatif")
        self.quantite_stock = new_quantity
        self.save(update_fields=['quantite_stock'])
    
    @property
    def stock_critique(self):
        """Return True if stock is below alert threshold."""
        return self.quantite_stock <= self.seuil_alerte
    
    @property
    def benefice_unitaire(self):
        """Calculate unit profit."""
        return self.prix_vente - self.prix_achat
    
    @property
    def marge_pourcentage(self):
        """Calculate profit margin percentage."""
        if self.prix_achat > 0:
            return ((self.prix_vente - self.prix_achat) / self.prix_achat) * 100
        return 0