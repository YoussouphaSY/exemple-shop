from rest_framework import serializers
from .models import MouvementStock, Inventaire, InventaireItem


class MouvementStockSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    utilisateur_nom = serializers.CharField(source='utilisateur.get_full_name', read_only=True)
    
    class Meta:
        model = MouvementStock
        fields = '__all__'


class InventaireItemSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    ecart = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = InventaireItem
        fields = '__all__'


class InventaireSerializer(serializers.ModelSerializer):
    items = InventaireItemSerializer(many=True, read_only=True)
    utilisateur_nom = serializers.CharField(source='utilisateur.get_full_name', read_only=True)
    
    class Meta:
        model = Inventaire
        fields = '__all__'