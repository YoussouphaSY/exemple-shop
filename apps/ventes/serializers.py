from rest_framework import serializers
from .models import Vente, VenteItem


class VenteItemSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    
    class Meta:
        model = VenteItem
        fields = '__all__'


class VenteSerializer(serializers.ModelSerializer):
    items = VenteItemSerializer(many=True, read_only=True)
    vendeur_nom = serializers.CharField(source='vendeur.get_full_name', read_only=True)
    
    class Meta:
        model = Vente
        fields = '__all__'