from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Vente, VenteItem


class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = ['client', 'telephone_client', 'mode_paiement', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('client', css_class='form-group col-md-6'),
                Column('telephone_client', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'mode_paiement',
            'note',
            Submit('submit', 'Sauvegarder', css_class='btn btn-primary')
        )


class VenteItemForm(forms.ModelForm):
    class Meta:
        model = VenteItem
        fields = ['produit', 'quantite', 'prix_unitaire']
        widgets = {
            'prix_unitaire': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produit'].queryset = self.fields['produit'].queryset.filter(actif=True)


VenteItemFormSet = inlineformset_factory(
    Vente, VenteItem,
    form=VenteItemForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)