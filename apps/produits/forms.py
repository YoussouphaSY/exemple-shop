from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Produit, Categorie


class ProduitQuickForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'categorie', 'prix_achat', 'prix_vente', 'quantite_stock']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit'}),
            'prix_achat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0'}),
            'prix_vente': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0'}),
            'quantite_stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
        }


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'categorie', 'description', 'prix_achat', 'prix_vente', 
                 'quantite_stock', 'seuil_alerte', 'image', 'actif']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'prix_achat': forms.NumberInput(attrs={'step': '0.01'}),
            'prix_vente': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('nom', css_class='form-group col-md-6'),
                Column('categorie', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'description',
            Row(
                Column('prix_achat', css_class='form-group col-md-6'),
                Column('prix_vente', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('quantite_stock', css_class='form-group col-md-6'),
                Column('seuil_alerte', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'image',
            'actif',
            Submit('submit', 'Sauvegarder', css_class='btn btn-primary')
        )


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Sauvegarder', css_class='btn btn-primary'))