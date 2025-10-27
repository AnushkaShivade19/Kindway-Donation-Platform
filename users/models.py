# users/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings # Use settings.AUTH_USER_MODEL
from donations.models import Category

# CustomUser remains the same as before
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
      ('DONOR', 'Donor'),
      ('NGO', 'NGO'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

class NGOProfile(models.Model):
    VERIFICATION_CHOICES = (
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    ngo_name = models.CharField(max_length=255)
    address = models.TextField()
    mission_statement = models.TextField(blank=True)
    
    # --- New Fields ---
    # Stores the uploaded government registration document
    document = models.FileField(upload_to='ngo_docs/', null=True, blank=True)

    # Admin verification status
    verification_status = models.CharField(
        max_length=10, 
        choices=VERIFICATION_CHOICES, 
        default='PENDING'
    )
    is_verification_email_sent = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    accepted_categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return self.ngo_name


# DonorProfile remains the same as before
class DonorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True)
    
    # --- Add these new fields ---
    pincode = models.CharField(max_length=10, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.full_name