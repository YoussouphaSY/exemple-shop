from rest_framework import serializers
from .models import Transaction, Budget, CaisseFonds


class TransactionSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.CharField(source='utilisateur.get_full_name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    categorie_display = serializers.CharField(source='get_categorie_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'


class BudgetSerializer(serializers.ModelSerializer):
    montant_realise = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    ecart = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    pourcentage_realise = serializers.FloatField(read_only=True)
    utilisateur_nom = serializers.CharField(source='utilisateur.get_full_name', read_only=True)
    
    class Meta:
        model = Budget
        fields = '__all__'


class CaisseFondsSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.CharField(source='utilisateur.get_full_name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = CaisseFonds
        fields = '__all__'