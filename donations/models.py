# donations/models.py

from django.db import models
from django.conf import settings # To link to our CustomUser

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True) # e.g., Food, Clothes, Books

    def __str__(self):
        return self.name
class NGORequest(models.Model):
    """Represents a specific need posted by an NGO."""
    ngo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} requested by {self.ngo.ngoprofile.ngo_name}"
    
class Donation(models.Model):
    STATUS_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('PENDING', 'Pending Pickup'),
        ('COMPLETED', 'Completed'),
    )
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='donation_images/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='AVAILABLE')
    created_at = models.DateTimeField(auto_now_add=True)

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='requested_donations',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    def __str__(self):
        return f"{self.title} by {self.donor.username}"
    
class DonationOffer(models.Model):
    STATUS_CHOICES = (
      ('PENDING', 'Pending'),
      ('ACCEPTED', 'Accepted'),
      ('REJECTED', 'Rejected'),
    )
    DELIVERY_CHOICES = (
        ('PICKUP', 'I require pickup'),
        ('DROP_OFF', 'I will drop off the item'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='offer_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    
    # Links to the users
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_offers', on_delete=models.CASCADE)
    ngo = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_offers', on_delete=models.CASCADE)

    # Status and Logistics
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offer from {self.donor.username} to {self.ngo.username}"