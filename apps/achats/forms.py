from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Achat, AchatItem, Fournisseur


class FournisseurQuickForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'contact', 'telephone', 'email']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du fournisseur'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Personne de contact'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+221 XX XXX XX XX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@fournisseur.com'}),
        }


class AchatForm(forms.ModelForm):
    class Meta:
        model = Achat
        fields = ['fournisseur', 'date_livraison', 'statut', 'note']
        widgets = {
            'date_livraison': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fournisseur'].queryset = Fournisseur.objects.filter(actif=True)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('fournisseur', css_class='form-group col-md-6'),
                Column('statut', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'date_livraison',
            'note',
            Submit('submit', 'Sauvegarder', css_class='btn btn-primary')
        )


class AchatItemForm(forms.ModelForm):
    class Meta:
        model = AchatItem
        fields = ['produit', 'quantite', 'quantite_recue', 'prix_unitaire']
        widgets = {
            'prix_unitaire': forms.NumberInput(attrs={'step': '0.01'}),
        }


AchatItemFormSet = inlineformset_factory(
    Achat, AchatItem,
    form=AchatItemForm,
    extra=1,  # Une ligne vide par défaut
    min_num=0, # Pas de minimum forcé en plus de l'extra
    validate_min=True,
    can_delete=True
)


class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'contact', 'telephone', 'email', 'adresse', 'actif']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('nom', css_class='form-group col-md-6'),
                Column('contact', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('telephone', css_class='form-group col-md-6'),
                Column('email', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'adresse',
            'actif',
            Submit('submit', 'Sauvegarder', css_class='btn btn-primary')
        )