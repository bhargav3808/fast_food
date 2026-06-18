# food_app/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import DeliveryAddress

class UserSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    pass


class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['street_address', 'city', 'postal_code', 'phone', 'is_default']
        widgets = {
            'street_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }