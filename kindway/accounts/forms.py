from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class DonorRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'contact_number', 'address', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'donor'
        if commit:
            user.save()
        return user


class NGORegistrationForm(UserCreationForm):
    ngo_name = forms.CharField(max_length=100, required=True)
    registration_id = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'contact_number', 'address', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'ngo'
        if commit:
            user.save()
        return user
