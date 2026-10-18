from django import forms
from .models import Order, Product, Review


class OrderCreateForm(forms.ModelForm):
  gift_card_code = forms.CharField(
      required=False,
      label="Код подарочной карты (если есть)",
      widget=forms.TextInput(
          attrs={
              "class": "form-control rounded-pill px-3",
              "placeholder": "Например: GB-A1B2C3D4",
          }
      ),
  )

  class Meta:
    model = Order
    fields = ["first_name", "last_name", "phone", "address"]
    widgets = {
        "first_name": forms.TextInput(
            attrs={"class": "form-control rounded-pill px-3"}
        ),
        "last_name": forms.TextInput(
            attrs={"class": "form-control rounded-pill px-3"}
        ),
        "phone": forms.TextInput(
            attrs={
                "class": "form-control rounded-pill px-3",
                "placeholder": "+7 (999) 000-00-00",
            }
        ),
        "address": forms.TextInput(
            attrs={
                "class": "form-control rounded-pill px-3",
                "placeholder": "Город, улица, дом, квартира",
            }
        ),
    }


class ReviewForm(forms.ModelForm):

  class Meta:
    model = Review
    fields = ["rating", "text"]
    widgets = {
        "rating": forms.Select(
            choices=[(i, f"⭐️ {i}") for i in range(5, 0, -1)],
            attrs={"class": "form-select rounded-pill px-3"},
        ),
        "text": forms.Textarea(
            attrs={
                "class": "form-control rounded-3",
                "rows": 3,
                "placeholder": "Поделитесь впечатлениями о товаре...",
            }
        ),
    }


class SellerProductForm(forms.ModelForm):

  class Meta:
    model = Product
    fields = [
        "category",
        "name",
        "brand",
        "price",
        "stock",
        "image",
        "description",
        "ingredients",
        "is_available",
    ]
    widgets = {
        "category": forms.Select(attrs={"class": "form-select"}),
        "name": forms.TextInput(attrs={"class": "form-control"}),
        "brand": forms.TextInput(attrs={"class": "form-control"}),
        "price": forms.NumberInput(attrs={"class": "form-control"}),
        "stock": forms.NumberInput(attrs={"class": "form-control"}),
        "image": forms.FileInput(attrs={"class": "form-control"}),
        "description": forms.Textarea(
            attrs={"class": "form-control", "rows": 3}
        ),
        "ingredients": forms.Textarea(
            attrs={"class": "form-control", "rows": 2}
        ),
        "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
    }
