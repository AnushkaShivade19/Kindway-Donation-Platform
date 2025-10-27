from django.db.models.signals import post_save
from django.dispatch import receiver
from donations.models import DonationOffer
from .models import Conversation

@receiver(post_save, sender=DonationOffer)
def create_conversation_on_acceptance(sender, instance, created, **kwargs):
    """
    Listens for a DonationOffer to be saved. If its status was just changed
    to 'ACCEPTED', it automatically creates a conversation.
    """
    # We only care about updates, not new offers being created.
    # And we only care if the status is now 'ACCEPTED'.
    if not created and instance.status == 'ACCEPTED':
        
        # Use get_or_create to safely create the conversation only once,
        # preventing any duplicates.
        conversation, conv_created = Conversation.objects.get_or_create(offer=instance)
        
        # If the conversation was just newly created...
        if conv_created:
            # Add the two participants (the donor and the NGO) to the conversation.
            conversation.participants.add(instance.donor, instance.ngo)
            print(f"Conversation created for offer: {instance.title}") # For debugging