from django.db import models
from django.conf import settings
from donations.models import DonationOffer

class Conversation(models.Model):
    """
    A conversation thread between a donor and an NGO,
    linked to a specific donation offer.
    """
    # The donation offer this conversation is about.
    offer = models.OneToOneField(DonationOffer, on_delete=models.CASCADE)
    
    # The users participating in the conversation.
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation about '{self.offer.title}'"

class Message(models.Model):
    """
    An individual message within a conversation.
    """
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp'] # Ensure messages are ordered chronologically

    def __str__(self):
        return f"From {self.sender.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"