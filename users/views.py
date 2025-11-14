from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

# Geopy Imports
from geopy.distance import great_circle
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Model Imports
from .models import CustomUser, Category, DonorProfile, NGOProfile
from donations.models import NGORequest

# Form Imports
from .forms import (
    DonorRegistrationForm, 
    NGORegistrationForm, 
    NGOProfileUpdateForm, 
    DonorProfileUpdateForm
)


# --- Helper Function ---
@login_required
def redirect_after_login(request):
    """
    Redirect users based on their 'user_type' attribute.
    """
    
    # This is the key line:
    # We check the 'user_type' field from your CustomUser model.
    if request.user.user_type == "NGO":
        return redirect('ngo_dashboard')  # Use the URL *name* if you have one
    
    elif request.user.user_type == "DONOR":
        return redirect('donor_dashboard')
        
    else:
        # A good fallback for superusers or other types
        if request.user.is_superuser:
            return redirect('/admin') 
        # Fallback for any other case
        return redirect('homepage')
        
def get_coords_from_pincode(pincode):
    """
    Helper function to get (latitude, longitude) from a pincode.
    """
    try:
        # Added a timeout to prevent hanging
        geolocator = Nominatim(user_agent="kindway_app", timeout=5) 
        location = geolocator.geocode(f"{pincode}, IN") # 'IN' limits search to India
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception as e:
        print(f"Error geocoding: {e}")
        return None

# --- Views ---

@login_required
def choose_user_role(request):
    """
    Allows a new user (especially from social auth) to choose their role.
    """
    if request.user.user_type:
        return redirect('dashboard')

    if request.method == 'POST':
        role = request.POST.get('role')
        user = request.user
        
        if role == 'DONOR':
            user.user_type = 'DONOR'
            DonorProfile.objects.get_or_create(user=user)
            user.save(update_fields=['user_type'])
            messages.success(request, "Your profile has been set up as a Donor!")
            return redirect('edit_donor_profile')
            
        elif role == 'NGO':
            user.user_type = 'NGO'
            user.save(update_fields=['user_type'])
            messages.info(request, "Great! Please complete your NGO profile details for verification.")
            return redirect('edit_ngo_profile')

    return render(request, 'users/choose_role.html')

@login_required
def edit_donor_profile(request):
    if request.user.user_type != 'DONOR':
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')
    
    try:
        donor_profile = request.user.donorprofile
    except DonorProfile.DoesNotExist:
        donor_profile = DonorProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = DonorProfileUpdateForm(request.POST, instance=donor_profile)
        if form.is_valid():
            form.save()
            user = request.user
            user.email = form.cleaned_data['email']
            user.save(update_fields=['email'])
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('dashboard')
    else:
        form = DonorProfileUpdateForm(instance=donor_profile, initial={'email': request.user.email})

    return render(request, 'users/edit_donor_profile.html', {'form': form})


def search_ngo(request):
    nearby_ngos = []
    searched_pincode = request.GET.get('pincode', '')
    searched_name = request.GET.get('name', '')
    radius = request.GET.get('radius', '25')

    base_query = CustomUser.objects.filter(
        user_type='NGO',
        ngoprofile__verification_status='VERIFIED'
    )

    if searched_name:
        base_query = base_query.filter(
            Q(ngoprofile__ngo_name__icontains=searched_name)
        )

    if searched_pincode:
        try:
            search_coords = get_coords_from_pincode(searched_pincode)
            radius = int(radius)
            
            if search_coords:
                for ngo_user in base_query:
                    if ngo_user.ngoprofile.latitude and ngo_user.ngoprofile.longitude:
                        ngo_coords = (ngo_user.ngoprofile.latitude, ngo_user.ngoprofile.longitude)
                        distance = great_circle(search_coords, ngo_coords).km
                        
                        if distance <= radius:
                            nearby_ngos.append({'user': ngo_user, 'distance': round(distance, 1)})
                
                nearby_ngos.sort(key=lambda x: x['distance'])
            else:
                messages.error(request, f"Could not find a location for pincode {searched_pincode}.")
        
        except (GeocoderTimedOut, GeocoderUnavailable):
            messages.error(request, "The location service is unavailable. Please try again later.")
    
    elif searched_name:
        for ngo_user in base_query:
            nearby_ngos.append({'user': ngo_user, 'distance': None}) 
        nearby_ngos.sort(key=lambda x: x['user'].ngoprofile.ngo_name)

    context = {
        'nearby_ngos': nearby_ngos,
        'searched_pincode': searched_pincode,
        'searched_name': searched_name,
        'selected_radius': radius,
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
        form = NGORegistrationForm(request.POST, request.FILES) 
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful! Your profile is pending verification.")
            return redirect('account_login')
    else:
        form = NGORegistrationForm()
        
    return render(request, 'users/register_ngo.html', {'form': form})

# --- THIS IS THE UPDATED VIEW ---
@login_required
def dashboard(request):
    
    # 1. NEW: Check for admin first
    if request.user.is_superuser:
        return redirect('admin:index') # This is the correct name for /admin/

    # 2. If user has no role, send them to choose one.
    if not request.user.user_type:
        return redirect('choose_user_role')

    # 3. Handle DONOR role
    if request.user.user_type == 'DONOR':
        try:
            donor_profile = request.user.donorprofile
            if not donor_profile.pincode:
                messages.info(request, "Please set your pincode to find nearby NGOs.")
                return redirect('edit_donor_profile')
        except DonorProfile.DoesNotExist:
            messages.warning(request, "Please complete your profile to get started.")
            return redirect('edit_donor_profile')
        
        nearby_requests = []
        if donor_profile.latitude and donor_profile.longitude:
            donor_coords = (donor_profile.latitude, donor_profile.longitude)
            all_requests = NGORequest.objects.filter(is_active=True).select_related('ngo__ngoprofile', 'category')
            for req in all_requests:
                if req.ngo.ngoprofile.latitude and req.ngo.ngoprofile.longitude:
                    ngo_coords = (req.ngo.ngoprofile.latitude, req.ngo.ngoprofile.longitude)
                    distance = great_circle(donor_coords, ngo_coords).km
                    if distance <= 50: # 50km radius
                        nearby_requests.append(req)
        
        return render(request, 'users/dashboard_donor.html', {'nearby_requests': nearby_requests})
    
    # 4. Handle NGO role
    elif request.user.user_type == 'NGO':
        try:
            ngo_profile = request.user.ngoprofile
            return render(request, 'users/dashboard_ngo.html', {'profile': ngo_profile})
        except NGOProfile.DoesNotExist:
            messages.info(request, "Welcome! Please complete your NGO profile details for verification.")
            return redirect('edit_ngo_profile')
    
    # 5. Fallback
    return redirect('index')


@login_required
def edit_ngo_profile(request):
    if not (request.user.user_type == 'NGO'):
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')
    
    ngo_profile, created = NGOProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = NGOProfileUpdateForm(request.POST, request.FILES, instance=ngo_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            user = request.user
            user.email = form.cleaned_data['email']
            user.save(update_fields=['email'])
            profile.save()
            form.save_m2m() 
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('dashboard')
    else:
        form = NGOProfileUpdateForm(instance=ngo_profile, initial={'email': request.user.email})

    return render(request, 'users/edit_ngo_profile.html', {'form': form})