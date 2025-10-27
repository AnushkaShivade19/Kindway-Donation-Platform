from django import forms
from .models import Donation

class DonationCreationForm(forms.ModelForm):
    class Meta:
        model = Donation
        # We only need the user to fill out these fields.
        # The 'donor' will be set automatically from the logged-in user.
        # The 'status' will default to 'AVAILABLE'.
        fields = ['title', 'description', 'category', 'image']

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add a nice prompt to the category dropdown
        self.fields['category'].empty_label = "Select a category"

from django import forms
from .models import DonationOffer, Category # Use DonationOffer
from .models import NGORequest

class NGORequestForm(forms.ModelForm):
    class Meta:
        model = NGORequest
        # The 'ngo' and 'is_active' fields will be set automatically in the view.
        fields = ['title', 'description', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select a category"
class DirectDonationOfferForm(forms.ModelForm):
    # This makes the choice field use radio buttons instead of a dropdown
    delivery_type = forms.ChoiceField(
        choices=DonationOffer.DELIVERY_CHOICES,
        widget=forms.RadioSelect,
        initial='DROP_OFF'
    )

    class Meta:
        model = DonationOffer
        fields = ['title', 'description', 'category', 'delivery_type', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select a category"