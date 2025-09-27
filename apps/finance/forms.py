from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Transaction, Budget, CaisseFonds


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'montant', 'categorie', 'description', 'date_valeur', 'piece_jointe', 'budget']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'date_valeur': forms.DateInput(attrs={'type': 'date'}),
            'montant': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('type', css_class='form-group col-md-6'),
                Column('categorie', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('montant', css_class='form-group col-md-6'),
                Column('date_valeur', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'description',
            'piece_jointe',
            Submit('submit', 'Sauvegarder', css_class='btn btn-primary')
        )


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['nom', 'description', 'montant_prevu', 'periode_debut', 'periode_fin', 'categories', 'actif']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'periode_debut': forms.DateInput(attrs={'type': 'date'}),
            'periode_fin': forms.DateInput(attrs={'type': 'date'}),
            'montant_prevu': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'nom',
            'description',
            Row(
                Column('montant_prevu', css_class='form-group col-md-4'),
                Column('periode_debut', css_class='form-group col-md-4'),
                Column('periode_fin', css_class='form-group col-md-4'),
                css_class='form-row'
            ),
            'categories',
            'actif',
            Submit('submit', 'Sauvegarder', css_class='btn btn-primary')
        )


class MouvementCaisseForm(forms.ModelForm):
    class Meta:
        model = CaisseFonds
        fields = ['type', 'montant', 'note']
        widgets = {
            'montant': forms.NumberInput(attrs={'step': '0.01'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('type', css_class='form-group col-md-6'),
                Column('montant', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'note',
            Submit('submit', 'Enregistrer mouvement', css_class='btn btn-primary')
        )


class RapportForm(forms.Form):
    date_debut = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date de début"
    )
    date_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date de fin"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('date_debut', css_class='form-group col-md-6'),
                Column('date_fin', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Submit('submit', 'Générer rapport', css_class='btn btn-primary')
        )