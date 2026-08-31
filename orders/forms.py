from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["nombre", "apellido", "dirección", "ciudad", "telefono", "metodo_pago"]