from django import forms
from .models import Donation, DonationOffer, NGORequest

# --- Form 1: For the "Available Donations" (if you have this feature) ---
class DonationCreationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['title', 'description', 'category', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select a category"
        # Make image not required
        if 'image' in self.fields:
            self.fields['image'].required = False

# --- Form 2: For an NGO to post a request ---
class NGORequestForm(forms.ModelForm):
    class Meta:
        model = NGORequest
        fields = ['title', 'description', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select a category"

# --- Form 3: For the "Offer a Donation" flow (This is the one we fixed) ---
class DirectDonationOfferForm(forms.ModelForm):
    
    # We remove the custom 'delivery_type' field from here.
    # By default, the ModelForm will now create a *single*
    # dropdown from the 'DELIVERY_CHOICES' on your model.
    # This fixes the double-dropdown bug.

    class Meta:
        model = DonationOffer
        # We list all fields the user should fill out.
        fields = ['title', 'description', 'category', 'delivery_type', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select a category"
        # Make image not required (matches model)
        if 'image' in self.fields:
            self.fields['image'].required = False