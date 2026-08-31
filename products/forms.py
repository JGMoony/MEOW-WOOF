from django import forms
from .models import Product, Review

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "category", "image"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].required = False

class ReviewForm(forms.ModelForm):
  class Meta:
    model = Review
    fields = ["rating", "comment"]
    widgets = {
      "rating": forms.Select(choices=Review.RATING_CHOICES),
      "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Escribe tu opinión..."}),
    }
