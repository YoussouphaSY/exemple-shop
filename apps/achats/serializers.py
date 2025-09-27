from rest_framework import serializers
from .models import Achat, AchatItem, Fournisseur


class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'


class AchatItemSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    
    class Meta:
        model = AchatItem
        fields = '__all__'


class AchatSerializer(serializers.ModelSerializer):
    items = AchatItemSerializer(many=True, read_only=True)
    fournisseur_nom = serializers.CharField(source='fournisseur.nom', read_only=True)
    utilisateur_nom = serializers.CharField(source='utilisateur.get_full_name', read_only=True)
    
    class Meta:
        model = Achat
        fields = '__all__'