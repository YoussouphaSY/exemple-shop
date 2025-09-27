from rest_framework import serializers
from .models import Produit, Categorie


class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = '__all__'


class ProduitSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    stock_critique = serializers.BooleanField(read_only=True)
    benefice_unitaire = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    marge_pourcentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Produit
        fields = '__all__'