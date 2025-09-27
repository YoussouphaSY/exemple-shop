from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Inventaire
from apps.produits.models import Produit


class InventaireForm(forms.ModelForm):
    class Meta:
        model = Inventaire
        fields = ['nom', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Créer inventaire', css_class='btn btn-primary'))


class AjustementStockForm(forms.Form):
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.filter(actif=True),
        label="Produit",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantite = forms.IntegerField(
        label="Quantité d'ajustement",
        help_text="Nombre positif pour ajouter, négatif pour retirer",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    motif = forms.CharField(
        label="Motif de l'ajustement",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'produit',
            Row(
                Column('quantite', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'motif',
            Submit('submit', 'Effectuer l\'ajustement', css_class='btn btn-warning')
        )