from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Type your message here...',
            })
        }
        labels = {
            'content': '' # Hides the label for a cleaner look
        }