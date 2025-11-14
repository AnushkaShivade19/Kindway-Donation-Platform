import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.hashers import make_password
from faker import Faker

# Import all your models
# Make sure your import paths are correct
from users.models import CustomUser, DonorProfile, NGOProfile
from donations.models import Category, Donation, DonationOffer, NGORequest
from communications.models import Event, SuccessStory
from messaging.models import Conversation, Message

class Command(BaseCommand):
    help = "Seeds the database with a rich set of fake data for testing."

    @transaction.atomic  # Ensures all operations succeed or none do
    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning old data...")
        # Clean database (but keep superusers)
        Message.objects.all().delete()
        Conversation.objects.all().delete()
        Event.objects.all().delete()
        DonationOffer.objects.all().delete()
        Donation.objects.all().delete()
        NGORequest.objects.all().delete()
        SuccessStory.objects.all().delete()
        CustomUser.objects.filter(is_superuser=False).delete()
        Category.objects.all().delete()
        
        self.stdout.write("Creating new data...")
        
        # Initialize Faker
        fake = Faker(['en_IN', 'en_US'])
        password = make_password('password123')

        # --- 1. Create Categories ---
        categories_list = [
            "Food", "Clothes", "Blood", "Books", "Toys", 
            "Saplings", "Electronics", "Furniture", "Medical Supplies"
        ]
        category_objs = []
        for cat_name in categories_list:
            cat = Category.objects.create(name=cat_name)
            category_objs.append(cat)
        self.stdout.write(f"Created {len(category_objs)} categories.")

        # --- 2. Create Users (Donors and NGOs) ---
        donors = []
        ngos = []

        # Create Donors
        for i in range(50):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.unique.email()
            
            user = CustomUser.objects.create(
                username=email,
                email=email,
                password=password,
                user_type='DONOR',
                first_name=first_name,
                last_name=last_name
            )
            DonorProfile.objects.create(
                user=user,
                full_name=f"{first_name} {last_name}",
                phone_number=fake.phone_number()[:20],
                pincode=fake.postcode(),
                latitude=fake.latitude(),
                longitude=fake.longitude()
            )
            donors.append(user)
        
        # Create NGOs
        for i in range(15):
            ngo_name = fake.company() + " Foundation"
            email = fake.unique.email()
            
            user = CustomUser.objects.create(
                username=email,
                email=email,
                password=password,
                user_type='NGO'
            )
            ngo_profile = NGOProfile.objects.create(
                user=user,
                ngo_name=ngo_name,
                address=fake.address().replace('\n', ', '),
                mission_statement=fake.paragraph(nb_sentences=3),
                verification_status=random.choice(['VERIFIED', 'PENDING']),
                latitude=fake.latitude(),
                longitude=fake.longitude()
            )
            # Assign some accepted categories randomly
            ngo_profile.accepted_categories.set(random.sample(category_objs, k=random.randint(1, 4)))
            ngos.append(user)
            
        self.stdout.write(f"Created {len(donors)} donors and {len(ngos)} NGOs.")
        
        # --- 3. Create NGO Requests ---
        verified_ngos = [u for u in ngos if u.ngoprofile.verification_status == 'VERIFIED']
        if verified_ngos:
            for ngo in verified_ngos:
                for _ in range(random.randint(1, 4)):
                    NGORequest.objects.create(
                        ngo=ngo,
                        category=random.choice(category_objs),
                        title=f"Urgent Need: {fake.bs().title()}",
                        description=fake.paragraph(nb_sentences=4),
                        is_active=True
                    )
            self.stdout.write("Created NGO requests.")
        
        # --- 4. Create Donations (Available Items) ---
        for donor in donors:
            for _ in range(random.randint(0, 3)):
                status = random.choice(['AVAILABLE', 'PENDING', 'COMPLETED'])
                Donation.objects.create(
                    donor=donor,
                    category=random.choice(category_objs),
                    title=f"Offering: {fake.word().capitalize()} {fake.word()}",
                    description=fake.paragraph(),
                    status=status,
                    requested_by=random.choice(ngos) if status != 'AVAILABLE' else None
                )
        self.stdout.write("Created available donation items.")

        # --- 5. Create Donation Offers (Direct) ---
        donation_offers = []
        if donors and verified_ngos:
            for _ in range(30): # Create 30 direct offers
                offer = DonationOffer.objects.create(
                    title=f"Offer of {fake.word()} for {fake.company()}",
                    description=fake.paragraph(),
                    category=random.choice(category_objs),
                    donor=random.choice(donors),
                    ngo=random.choice(verified_ngos),
                    status=random.choice(['PENDING', 'ACCEPTED', 'REJECTED']),
                    delivery_type=random.choice(['PICKUP', 'DROP_OFF'])
                )
                donation_offers.append(offer)
            self.stdout.write(f"Created {len(donation_offers)} direct donation offers.")

        # --- 6. Create Events ---
        if verified_ngos:
            for ngo in verified_ngos:
                for _ in range(random.randint(0, 2)):
                    event = Event.objects.create(
                        ngo=ngo,
                        title=f"{fake.word().capitalize()} Drive at {fake.city()}",
                        description=fake.paragraph(),
                        location=fake.address(),
                        event_date=fake.date_time_between(start_date='+1d', end_date='+60d', tzinfo=timezone.get_current_timezone())
                    )
                    # Add volunteers
                    event.volunteers.set(random.sample(donors, k=random.randint(1, 10)))
            self.stdout.write("Created events with volunteers.")

        # --- 7. Create Success Stories ---
        for _ in range(10):
            SuccessStory.objects.create(
                name=fake.name(),
                city=fake.city(),
                story_content=fake.paragraph(nb_sentences=10),
                is_featured=random.choice([True, False])
            )
        self.stdout.write("Created success stories.")
        
        # --- 8. Create Conversations and Messages ---
        for offer in donation_offers:
            # Create a conversation for the offer
            convo = Conversation.objects.create(offer=offer)
            convo.participants.add(offer.donor, offer.ngo)
            
            last_time = convo.created_at
            for _ in range(random.randint(2, 7)):
                sender = random.choice([offer.donor, offer.ngo])
                msg_time = last_time + timedelta(minutes=random.randint(5, 60 * 24))
                
                Message.objects.create(
                    conversation=convo,
                    sender=sender,
                    content=fake.sentence(),
                    is_read=random.choice([True, False]),
                    timestamp=msg_time  # Manually set timestamp
                )
                last_time = msg_time
            
            # Update the conversation's 'updated_at' field
            convo.updated_at = last_time
            convo.save()
        self.stdout.write("Created conversations and messages.")

        self.stdout.write(self.style.SUCCESS("\nDatabase successfully seeded!"))
        self.stdout.write(f"Test login with any user (e.g., 'donor1@example.com') and password 'password123'")