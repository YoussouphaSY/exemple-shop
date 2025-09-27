from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from apps.ventes.models import Vente
from apps.achats.models import Achat
from apps.stock.models import MouvementStock
from .models import Notification

User = get_user_model()


@receiver(post_save, sender=Vente)
def notification_nouvelle_vente(sender, instance, created, **kwargs):
    """Créer une notification lors d'une nouvelle vente."""
    if created:
        # Notifier les admins et managers
        admins = User.objects.filter(role__in=['admin', 'manager'])
        
        for admin in admins:
            Notification.objects.create(
                titre="Nouvelle vente",
                message=f"Vente {instance.numero} - {instance.total_ttc} FCFA par {instance.vendeur.get_full_name() if instance.vendeur else 'Système'}",
                type="success",
                utilisateur=admin,
                url=f"/ventes/{instance.pk}/"
            )


@receiver(post_save, sender=Achat)
def notification_nouvel_achat(sender, instance, created, **kwargs):
    """Créer une notification lors d'un nouvel achat."""
    if created:
        # Notifier les admins et managers
        admins = User.objects.filter(role__in=['admin', 'manager'])
        
        for admin in admins:
            Notification.objects.create(
                titre="Nouvel achat",
                message=f"Achat {instance.numero} - {instance.total_ttc} FCFA de {instance.fournisseur.nom}",
                type="info",
                utilisateur=admin,
                url=f"/achats/{instance.pk}/"
            )


@receiver(post_save, sender=MouvementStock)
def notification_stock_critique(sender, instance, created, **kwargs):
    """Notifier quand un produit atteint le stock critique."""
    if created and instance.produit.stock_critique:
        # Notifier les admins et managers
        admins = User.objects.filter(role__in=['admin', 'manager'])
        
        for admin in admins:
            Notification.objects.create(
                titre="Stock critique",
                message=f"Le produit {instance.produit.nom} a un stock critique ({instance.produit.quantite_stock} restants)",
                type="warning",
                utilisateur=admin,
                url=f"/produits/{instance.produit.slug}/"
            )