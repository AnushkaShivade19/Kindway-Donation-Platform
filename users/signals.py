# users/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import NGOProfile
from .models import NGOProfile, DonorProfile
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

@receiver(post_save, sender=DonorProfile)
def geocode_donor_pincode(sender, instance, **kwargs):
    """
    Automatically geocode the donor's pincode and save lat/long.
    """
    # Check if pincode was provided and coordinates are missing
    if instance.pincode and not (instance.latitude and instance.longitude):
        geolocator = Nominatim(user_agent="kindway_donor_geocoder")
        try:
            # Add ", India" for better accuracy
            location = geolocator.geocode(f"{instance.pincode}, India")
            if location:
                instance.latitude = location.latitude
                instance.longitude = location.longitude
                instance.save(update_fields=['latitude', 'longitude'])
        except (GeocoderTimedOut, GeocoderUnavailable):
            pass
        
@receiver(post_save, sender=NGOProfile)
def geocode_ngo_address(sender, instance, created, **kwargs):
    """
    Automatically geocode the NGO's address and save lat/long.
    This runs whenever an NGOProfile is saved.
    """
    # Check if address was provided and coordinates are missing
    if instance.address and not (instance.latitude and instance.longitude):
        geolocator = Nominatim(user_agent="kindway_app")
        try:
            location = geolocator.geocode(instance.address)
            if location:
                instance.latitude = location.latitude
                instance.longitude = location.longitude
                # Use update_fields to avoid triggering the signal again in a loop
                instance.save(update_fields=['latitude', 'longitude'])
        except (GeocoderTimedOut, GeocoderUnavailable):
            # Handle cases where the geocoding service is unavailable
            pass

# The @receiver decorator connects this function to the post_save signal
# for the NGOProfile model.
@receiver(post_save, sender=NGOProfile)
def send_verification_email(sender, instance, **kwargs):
    """
    Sends an email to the NGO when their profile is verified.
    """
    # Check if the NGO is verified AND if the email has NOT been sent yet
    if instance.verification_status == 'VERIFIED' and not instance.is_verification_email_sent:
        
        # Prepare email content
        subject = "Congratulations! Your Kindway NGO Profile is Verified!"
        ngo_user = instance.user
        
        # We will create these templates in the next step
        html_message = render_to_string('emails/ngo_verified.html', {'ngo_name': instance.ngo_name})
        plain_message = render_to_string('emails/ngo_verified.txt', {'ngo_name': instance.ngo_name})

        # Send the email
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL, # Sender's email
            [ngo_user.email],            # Recipient's email
            html_message=html_message,
            fail_silently=False,
        )

        # Mark that the email has been sent to prevent re-sending
        instance.is_verification_email_sent = True
        instance.save(update_fields=['is_verification_email_sent'])