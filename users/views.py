

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import DonorRegistrationForm, NGORegistrationForm

from geopy.distance import great_circle
from geopy.geocoders import Nominatim
from .models import CustomUser ,Category
from django.contrib import messages

from .forms import DonorRegistrationForm, NGORegistrationForm, NGOProfileUpdateForm, DonorProfileUpdateForm

# users/views.py
from .models import DonorProfile , NGOProfile# Import DonorProfile

@login_required
def choose_user_role(request):
    """
    Allows a new user (especially from social auth) to choose their role.
    """
    # If user already has a role, redirect them away.
    if request.user.user_type:
        return redirect('dashboard')

    if request.method == 'POST':
        role = request.POST.get('role')
        user = request.user
        
        if role == 'DONOR':
            user.user_type = 'DONOR'
            # Create a donor profile for them
            DonorProfile.objects.get_or_create(user=user)
            user.save(update_fields=['user_type'])
            messages.success(request, "Your profile has been set up as a Donor!")
            return redirect('edit_donor_profile') # Send them to fill out their pincode
            
        elif role == 'NGO':
            user.user_type = 'NGO'
            user.save(update_fields=['user_type'])
            
            # 2. Redirect to the EDIT profile page, not the register page
            messages.info(request, "Great! Please complete your NGO profile details for verification.")
            return redirect('edit_ngo_profile')

    return render(request, 'users/choose_role.html')

@login_required
def edit_donor_profile(request):
    # Security check to ensure the user is a donor
    if request.user.user_type != 'DONOR':
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')
    
    try:
        donor_profile = request.user.donorprofile
    except DonorProfile.DoesNotExist:
        # Handle cases where a profile might not exist (e.g., social auth user)
        donor_profile = DonorProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = DonorProfileUpdateForm(request.POST, instance=donor_profile)
        if form.is_valid():
            # Save the DonorProfile part of the form
            form.save()
            
            # Update the email on the CustomUser model
            user = request.user
            user.email = form.cleaned_data['email']
            user.save(update_fields=['email'])

            messages.success(request, "Your profile has been updated successfully!")
            return redirect('dashboard')
    else:
        # On a GET request, pre-populate the form with existing data
        form = DonorProfileUpdateForm(instance=donor_profile, initial={'email': request.user.email})

    return render(request, 'users/edit_donor_profile.html', {'form': form})

def search_ngo(request):
    nearby_ngos = []
    searched_pincode = ""

    if request.method == 'GET' and 'pincode' in request.GET:
        pincode = request.GET.get('pincode')
        radius = request.GET.get('radius', 25) # Default 25km radius
        searched_pincode = pincode

        if pincode and radius:
            geolocator = Nominatim(user_agent="kindway_app_search")
            try:
                # Geocode user's pincode
                user_location = geolocator.geocode(f"{pincode}, India")
                if user_location:
                    user_coords = (user_location.latitude, user_location.longitude)

                    # Filter for verified NGOs that have coordinates
                    verified_ngos = CustomUser.objects.filter(
                        user_type='NGO',
                        ngoprofile__verification_status='VERIFIED',
                        ngoprofile__latitude__isnull=False
                    )

                    for ngo_user in verified_ngos:
                        ngo_coords = (ngo_user.ngoprofile.latitude, ngo_user.ngoprofile.longitude)
                        distance = great_circle(user_coords, ngo_coords).km
                        
                        if distance <= float(radius):
                            nearby_ngos.append({
                                'user': ngo_user,
                                'distance': round(distance, 1)
                            })
                    
                    # Sort NGOs by distance
                    nearby_ngos.sort(key=lambda x: x['distance'])

            except (GeocoderTimedOut, GeocoderUnavailable):
                messages.error(request, "The location service is currently unavailable. Please try again later.")

    context = {
        'nearby_ngos': nearby_ngos,
        'searched_pincode': searched_pincode
    }
    return render(request, 'users/search_ngo.html', context)
def donor_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            return redirect('dashboard')
    else:
        form = DonorRegistrationForm()
        
    return render(request, 'users/register_donor.html', {'form': form})

def ngo_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        # We pass request.FILES to handle the file upload
        form = NGORegistrationForm(request.POST, request.FILES) 
        if form.is_valid():
            user = form.save()
            # We don't log in the NGO. They must wait for verification.
            # We can add a "pending verification" page later.
            # For now, redirect to login with a success message.
            return redirect('account_login') # This is an allauth URL
    else:
        form = NGORegistrationForm()
        
    return render(request, 'users/register_ngo.html', {'form': form})

from donations.models import NGORequest # <-- Import NGORequest
from geopy.distance import great_circle # <-- Import great_circle

# users/views.py

@login_required
def dashboard(request):
    # 1. If user has no role, send them to choose one.
    if not request.user.user_type:
        return redirect('choose_user_role')

    # 2. Handle DONOR role
    if request.user.user_type == 'DONOR':
        try:
            donor_profile = request.user.donorprofile
            if not donor_profile.pincode:
                messages.info(request, "Please set your pincode to find nearby NGOs.")
                return redirect('edit_donor_profile')
        except DonorProfile.DoesNotExist:
            messages.warning(request, "Please complete your profile to get started.")
            return redirect('edit_donor_profile')
        
        # ... (The rest of your donor dashboard logic is correct)
        nearby_requests = []
        if donor_profile.latitude and donor_profile.longitude:
            donor_coords = (donor_profile.latitude, donor_profile.longitude)
            all_requests = NGORequest.objects.filter(is_active=True).select_related('ngo__ngoprofile', 'category')
            for req in all_requests:
                if req.ngo.ngoprofile.latitude and req.ngo.ngoprofile.longitude:
                    ngo_coords = (req.ngo.ngoprofile.latitude, req.ngo.ngoprofile.longitude)
                    distance = great_circle(donor_coords, ngo_coords).km
                    if distance <= 50:
                        nearby_requests.append(req)
        
        return render(request, 'users/dashboard_donor.html', {'nearby_requests': nearby_requests})
    
    # 3. Handle NGO role
    elif request.user.user_type == 'NGO':
        try:
            # This is the only place we should check for the profile.
            ngo_profile = request.user.ngoprofile
            # If we find it, we render the dashboard, no matter the verification status.
            # The template will handle showing the right message.
            return render(request, 'users/dashboard_ngo.html', {'profile': ngo_profile})
        except NGOProfile.DoesNotExist:
            # This case is ONLY for new Google users who have chosen the NGO role
            # but have not yet filled out their profile details.
            messages.info(request, "Welcome! Please complete your NGO profile details for verification.")
            return redirect('edit_ngo_profile')
    
    # 4. Fallback
    return redirect('index')

from .forms import NGOProfileUpdateForm # Add this import

@login_required
def edit_ngo_profile(request):
    # Security check: Ensure user is a verified NGO
    if not (request.user.user_type == 'NGO'):
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')
    
    ngo_profile, created = NGOProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Pass 'instance' to pre-fill the form with existing data
        form = NGOProfileUpdateForm(request.POST, instance=ngo_profile)
        if form.is_valid():
            # Save the NGOProfile part
            profile = form.save(commit=False)
            
            # Save the email on the CustomUser model
            user = request.user
            user.email = form.cleaned_data['email']
            user.save(update_fields=['email'])
            
            # Save the NGOProfile with its many-to-many relationships
            profile.save()
            form.save_m2m() # Required for saving ManyToManyField

            messages.success(request, "Your profile has been updated successfully!")
            return redirect('dashboard')
    else:
        # For a GET request, initialize the form with the user's current data
        form = NGOProfileUpdateForm(instance=ngo_profile, initial={'email': request.user.email})

    return render(request, 'users/edit_ngo_profile.html', {'form': form})