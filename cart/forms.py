from django import forms

class CartItemUpdateForm(forms.Form):
    item_id = forms.IntegerField(widget=forms.HiddenInput)
    quantity = forms.IntegerField(min_value=1)

class SelectAllForm(forms.Form):
    select = forms.BooleanField(required=False, initial=True)