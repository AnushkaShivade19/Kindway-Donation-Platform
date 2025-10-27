# users/forms.py

from django import forms
from django.db import transaction
from .models import CustomUser, DonorProfile, NGOProfile
from donations.models import Category

class DonorRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(max_length=255, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    pincode = forms.CharField(max_length=10, required=True) # <-- Add this line
    
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email']

    def clean_email(self):
        """
        Validates that the email is not already in use.
        """
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email
    @transaction.atomic
    def save(self):
        user = CustomUser.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            user_type='DONOR'
        )
        
        DonorProfile.objects.create(
            user=user,
            full_name=self.cleaned_data['full_name'],
            phone_number=self.cleaned_data['phone_number'],
            pincode=self.cleaned_data['pincode'] # <-- Add this line
        )
        return user

class NGORegistrationForm(forms.ModelForm):
    # Fields from CustomUser
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    
    # Fields from NGOProfile
    # We can just use the Meta class for this one
    class Meta:
        model = NGOProfile
        fields = ['ngo_name', 'address', 'mission_statement', 'document']

    @transaction.atomic
    def save(self):
        # Create the CustomUser
        user = CustomUser.objects.create_user(
            username=self.cleaned_data['email'], # Use email as username
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            user_type='NGO'
        )
        
        # Create the NGOProfile
        NGOProfile.objects.create(
            user=user,
            ngo_name=self.cleaned_data['ngo_name'],
            address=self.cleaned_data['address'],
            mission_statement=self.cleaned_data['mission_statement'],
            document=self.cleaned_data['document']
            # verification_status defaults to 'PENDING'
        )
        return user
    
class NGOProfileUpdateForm(forms.ModelForm):
    # This field will edit the email on the CustomUser model.
    email = forms.EmailField(required=True)
    
    # This makes the categories a user-friendly set of checkboxes.
    accepted_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = NGOProfile
        fields = ['ngo_name', 'address', 'mission_statement', 'accepted_categories']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'mission_statement': forms.Textarea(attrs={'rows': 3}),
        }
class DonorProfileUpdateForm(forms.ModelForm):
    # Field from the CustomUser model
    email = forms.EmailField(required=True)

    class Meta:
        model = DonorProfile
        # Fields from the DonorProfile model
        fields = ['full_name', 'pincode', 'phone_number']