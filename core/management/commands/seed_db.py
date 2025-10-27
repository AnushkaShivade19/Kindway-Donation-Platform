import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from faker import Faker

# Import all your models
from users.models import CustomUser, DonorProfile, NGOProfile
from donations.models import Category, DonationOffer, NGORequest
from communications.models import Event

# Define the number of dummy records you want
NUM_USERS = 5
NUM_OFFERS = 5
NUM_REQUESTS = 5
NUM_EVENTS = 5

class Command(BaseCommand):
    help = "Seeds the database with fake data for testing."

    @transaction.atomic # Ensures all operations succeed or none do
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        # Clear existing data (optional, but recommended for clean seeding)
        CustomUser.objects.exclude(is_superuser=True).delete()
        Category.objects.all().delete()
        # Profiles, Offers, Requests, Events will cascade delete

        self.stdout.write("Creating new data...")
        
        # Initialize Faker
        # Using 'en_IN' for Indian names, addresses, pincodes
        fake = Faker('en_IN')

        # --- 1. Create Categories ---
        categories = [
            "Food", "Clothes", "Blood", "Books", "Toys", 
            "Saplings", "Electronics", "Furniture"
        ]
        category_objs = []
        for cat_name in categories:
            cat = Category.objects.create(name=cat_name)
            category_objs.append(cat)
        self.stdout.write(f"Created {len(category_objs)} categories.")

        # --- 2. Create Users (Donors and NGOs) ---
        donors = []
        ngos = []

        # Create Donors
        for _ in range(NUM_USERS):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.unique.email()
            username = email # Use email as username
            
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password='password123', # Use a fixed password for easy testing
                user_type='DONOR',
                first_name=first_name,
                last_name=last_name
            )
            
            # Create Donor Profile
            DonorProfile.objects.create(
                user=user,
                full_name=f"{first_name} {last_name}",
                phone_number=fake.phone_number(),
                pincode=fake.postcode() # Geocoding signal will handle lat/long
            )
            donors.append(user)
        self.stdout.write(f"Created {len(donors)} donors with profiles.")

        # Create NGOs
        for _ in range(NUM_USERS):
            ngo_name = fake.company() + " Foundation"
            email = fake.unique.email()
            username = email
            
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password='password123',
                user_type='NGO'
            )
            
            # Create NGO Profile
            ngo_profile = NGOProfile.objects.create(
                user=user,
                ngo_name=ngo_name,
                address=fake.address().replace('\n', ', '),
                mission_statement=fake.paragraph(nb_sentences=3),
                # Assume verification happens later, or set randomly:
                verification_status=random.choice(['VERIFIED', 'PENDING']),
                # Document upload is skipped for dummy data
            )
            
            # Assign some accepted categories randomly
            num_cats = random.randint(1, 4)
            ngo_profile.accepted_categories.set(random.sample(category_objs, num_cats))
            ngos.append(user)
        self.stdout.write(f"Created {len(ngos)} NGOs with profiles.")
        # Note: Geocoding signals should run automatically when profiles are saved.

        # --- 3. Create Donation Offers ---
        verified_ngos = [u for u in ngos if hasattr(u, 'ngoprofile') and u.ngoprofile.verification_status == 'VERIFIED']
        if donors and verified_ngos:
            for _ in range(NUM_OFFERS):
                donor = random.choice(donors)
                ngo = random.choice(verified_ngos)
                category = random.choice(category_objs)
                
                DonationOffer.objects.create(
                    title=f"{category.name} Donation Offer",
                    description=fake.paragraph(nb_sentences=2),
                    category=category,
                    donor=donor,
                    ngo=ngo,
                    status=random.choice(['PENDING', 'ACCEPTED', 'REJECTED']),
                    delivery_type=random.choice(['PICKUP', 'DROP_OFF'])
                    # Image field is skipped
                )
            self.stdout.write(f"Created {NUM_OFFERS} donation offers.")
        else:
            self.stdout.write("Skipping donation offers (no donors or verified NGOs found).")


        # --- 4. Create NGO Requests ---
        if verified_ngos:
            for _ in range(NUM_REQUESTS):
                ngo = random.choice(verified_ngos)
                category = random.choice(category_objs)
                
                NGORequest.objects.create(
                    ngo=ngo,
                    category=category,
                    title=f"Request for {category.name}",
                    description=fake.paragraph(nb_sentences=2),
                    is_active=random.choice([True, False])
                )
            self.stdout.write(f"Created {NUM_REQUESTS} NGO requests.")
        else:
             self.stdout.write("Skipping NGO requests (no verified NGOs found).")

        # --- 5. Create Events ---
        if verified_ngos:
            for _ in range(NUM_EVENTS):
                ngo = random.choice(verified_ngos)
                
                Event.objects.create(
                    ngo=ngo,
                    title=fake.sentence(nb_words=4).replace('.', ' Drive'),
                    description=fake.paragraph(nb_sentences=3),
                    location=fake.street_address(),
                    event_date=timezone.now() + timedelta(days=random.randint(5, 60))
                )
            self.stdout.write(f"Created {NUM_EVENTS} events.")
        else:
            self.stdout.write("Skipping events (no verified NGOs found).")


        self.stdout.write(self.style.SUCCESS("Database successfully seeded!"))
    
