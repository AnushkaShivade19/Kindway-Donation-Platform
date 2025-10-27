from django import forms
from .models import Event , SuccessStory

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'event_date']
        widgets = {
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
class SuccessStoryForm(forms.ModelForm):
    class Meta:
        model = SuccessStory
        fields = ['name', 'city', 'story_content']
        widgets = {
            'story_content': forms.Textarea(attrs={'rows': 5}),
        }