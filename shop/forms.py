from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):

  class Meta:
    model = Order
    fields = ['first_name', 'last_name', 'phone', 'address']
    widgets = {
        'first_name': forms.TextInput(attrs={'class': 'form-control'}),
        'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        'phone': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '+7 (999) 000-00-00'}
        ),
        'address': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'г. Москва, ул...'}
        ),
    }