from django import forms

from .models import PurchaseItem, Purchase


# Purchase item form
class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ('product', 'quantity')


# Purchase Form
class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ('supplier', 'tax', 'state', 'delivery_date')


# Formset para PurchaseItem con lógica de validación personalizada
class PurchaseItemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()