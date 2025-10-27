from django.db import models
from django.conf import settings

class Event(models.Model):
    ngo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    event_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    # This field will track all the users who have signed up to volunteer.
    volunteers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='volunteered_events', blank=True)

    def __str__(self):
        return self.title
    
class SuccessStory(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    story_content = models.TextField()
    is_featured = models.BooleanField(default=False) # For admin to choose which ones go on homepage
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Story from {self.name} ({self.city})"