from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from geopy.distance import great_circle

from .models import DonationOffer, NGORequest, Category
from .forms import DirectDonationOfferForm, NGORequestForm
from users.models import CustomUser, DonorProfile

@login_required
def offer_donation_flow(request):
    """Handles the 2-step process for a donor to offer an item to a specific NGO."""
    nearby_ngos = []
    other_ngos = []  # A list for NGOs that are far away or un-sortable
    context = {'state': 'initial_form'}

    if request.method == 'POST':
        form = DirectDonationOfferForm(request.POST, request.FILES)
        if form.is_valid():
            # Step 1: Temporarily save donation details in the session
            request.session['donation_offer_data'] = {
                'title': form.cleaned_data['title'],
                'description': form.cleaned_data['description'],
                'category_id': form.cleaned_data['category'].id,
                'delivery_type': form.cleaned_data['delivery_type'],
            }
            # Note: Storing image in session is tricky. This flow assumes
            # you are re-uploading or handling it differently.
            # For simplicity, we'll skip the image in the session for now.

            # Step 2: Try to get donor's location (but don't require it)
            donor_coords = None
            try:
                donor_profile = request.user.donorprofile
                if donor_profile.latitude and donor_profile.longitude:
                    donor_coords = (donor_profile.latitude, donor_profile.longitude)
                else:
                    # Add a message if pincode is missing, but don't block
                    messages.info(request, "Set your pincode in your profile to see nearby NGOs first.")
            except DonorProfile.DoesNotExist:
                messages.error(request, "Please complete your profile to proceed.")
                return redirect('edit_donor_profile') # Still block if no profile at all

            category = form.cleaned_data['category']
            relevant_ngos = CustomUser.objects.filter(
                user_type='NGO',
                ngoprofile__verification_status='VERIFIED',
                ngoprofile__accepted_categories=category,
                ngoprofile__latitude__isnull=False # Ensure NGO has a location
            ).distinct()

            if donor_coords:
                # --- Location is known: Sort into "nearby" and "other" ---
                for ngo_user in relevant_ngos:
                    ngo_coords = (ngo_user.ngoprofile.latitude, ngo_user.ngoprofile.longitude)
                    distance = great_circle(donor_coords, ngo_coords).km
                    ngo_data = {'user': ngo_user, 'distance': round(distance, 1)}
                    
                    if distance <= 50: # 50km radius
                        nearby_ngos.append(ngo_data)
                    else:
                        other_ngos.append(ngo_data)
                
                # Sort both lists by distance
                nearby_ngos.sort(key=lambda x: x['distance'])
                other_ngos.sort(key=lambda x: x['distance'])
            
            else:
                # --- Location is unknown: Put all NGOs in "other" list ---
                for ngo_user in relevant_ngos:
                    # No distance to calculate
                    other_ngos.append({'user': ngo_user, 'distance': None})
                
                # Sort by name as a fallback
                other_ngos.sort(key=lambda x: x['user'].ngoprofile.ngo_name)

            # Step 3: Update template context
            context['state'] = 'show_ngos'
            context['nearby_ngos'] = nearby_ngos
            context['other_ngos'] = other_ngos
            context['form'] = form # Pass the form again for display

    else: # GET request
        form = DirectDonationOfferForm()

    context['form'] = form
    return render(request, 'donations/offer_donation.html', context)


@login_required
def send_offer_to_ngo(request, ngo_id):
    """Finalizes the donation by creating a DonationOffer from session data."""
    if request.method == 'POST' and 'donation_offer_data' in request.session:
        offer_data = request.session.pop('donation_offer_data')
        ngo = get_object_or_404(CustomUser, id=ngo_id, user_type='NGO')
        
        DonationOffer.objects.create(
            donor=request.user,
            ngo=ngo,
            title=offer_data['title'],
            description=offer_data['description'],
            category_id=offer_data['category_id'],
            delivery_type=offer_data['delivery_type'],
        )
        messages.success(request, f"Your donation offer has been sent to {ngo.ngoprofile.ngo_name}!")
        return redirect('dashboard')
    
    # If session data is gone or it's a GET request, send back to start
    messages.error(request, "Your session expired. Please start the offer again.")
    return redirect('offer_donation_flow')


@login_required
def offer_history(request):
    """Shows the logged-in donor a list of their sent donation offers."""
    sent_offers = DonationOffer.objects.filter(donor=request.user).order_by('-created_at')
    return render(request, 'donations/offer_history.html', {'sent_offers': sent_offers})


@login_required
def offer_detail(request, offer_id):
    """Shows the detail page for a single donation offer."""
    offer = get_object_or_404(DonationOffer, id=offer_id)
    # Security check: only participants can view the offer
    if request.user != offer.donor and request.user != offer.ngo:
        return HttpResponseForbidden("You do not have permission to view this page.")
    return render(request, 'donations/offer_detail.html', {'offer': offer})


@login_required
def ngo_offer_list(request):
    """Shows a verified NGO a list of donation offers they have received."""
    if not (request.user.user_type == 'NGO' and hasattr(request.user, 'ngoprofile') and request.user.ngoprofile.verification_status == 'VERIFIED'):
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')
    
    received_offers = DonationOffer.objects.filter(ngo=request.user).order_by('-created_at')
    return render(request, 'donations/ngo_offer_list.html', {'received_offers': received_offers})


@login_required
def update_offer_status(request, offer_id, new_status):
    """Handles an NGO's action to accept or reject an offer."""
    if request.method != 'POST':
        return redirect('dashboard')
    
    offer = get_object_or_404(DonationOffer, id=offer_id)
    if request.user != offer.ngo:
        return HttpResponseForbidden("You cannot change the status of this offer.")

    if new_status == 'accept' and offer.status == 'PENDING':
        offer.status = 'ACCEPTED'
        messages.success(request, f"You have accepted the offer for '{offer.title}'.")
    elif new_status == 'reject' and offer.status == 'PENDING':
        offer.status = 'REJECTED'
        messages.warning(request, f"You have rejected the offer for '{offer.title}'.")
    
    offer.save(update_fields=['status'])
    return redirect('ngo_offer_list')


@login_required
def create_ngo_request(request):
    """Allows a verified NGO to post a specific "need" to the platform."""
    if not (request.user.user_type == 'NGO' and hasattr(request.user, 'ngoprofile') and request.user.ngoprofile.verification_status == 'VERIFIED'):
        messages.error(request, "Only verified NGOs can post requests.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = NGORequestForm(request.POST)
        if form.is_valid():
            ngo_request = form.save(commit=False)
            ngo_request.ngo = request.user
            ngo_request.save()
            messages.success(request, "Your request for an item has been posted!")
            return redirect('dashboard')
    else:
        form = NGORequestForm()
    return render(request, 'donations/create_ngo_request.html', {'form': form})


@login_required
def fulfill_ngo_request(request, request_id):
    """Allows a donor to respond directly to an NGO's "need"."""
    ngo_request = get_object_or_404(NGORequest, id=request_id)

    if request.method == 'POST':
        form = DirectDonationOfferForm(request.POST, request.FILES)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.donor = request.user
            offer.ngo = ngo_request.ngo # Recipient is the NGO who made the request
            offer.save()
            messages.success(request, f"Your offer has been sent to {ngo_request.ngo.ngoprofile.ngo_name}!")
            return redirect('dashboard')
    else:
        # Pre-populate the form with info from the NGO's request
        initial_data = {'title': f"Response to: {ngo_request.title}", 'category': ngo_request.category}
        form = DirectDonationOfferForm(initial=initial_data)
    
    return render(request, 'donations/fulfill_request.html', {'form': form, 'ngo_request': ngo_request})


# --- ADD THESE TWO VIEWS ---

@login_required
def donate_to_ngo_view(request, ngo_id):
    """
    Shows a form for a donor to donate directly to a specific NGO
    (from the search_ngo page).
    """
    ngo = get_object_or_404(CustomUser, id=ngo_id, user_type='NGO')

    if request.method == 'POST':
        form = DirectDonationOfferForm(request.POST, request.FILES)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.donor = request.user
            offer.ngo = ngo # Set the NGO directly
            offer.save()
            messages.success(request, f"Your offer has been sent to {ngo.ngoprofile.ngo_name}!")
            return redirect('dashboard')
    else:
        # Pre-populate the title to make it clear
        initial_data = {'title': f"Donation for {ngo.ngoprofile.ngo_name}"}
        form = DirectDonationOfferForm(initial=initial_data)
    
    return render(request, 'donations/donate_to_ngo.html', {'form': form, 'ngo': ngo})


@login_required
def view_ngo_requests(request, ngo_id):
    """
    Shows a list of all active requests from a single NGO
    (from the search_ngo page).
    """
    ngo = get_object_or_404(CustomUser, id=ngo_id, user_type='NGO')
    ngo_requests = NGORequest.objects.filter(
        ngo=ngo, 
        is_active=True
    ).order_by('-created_at')
    
    return render(request, 'donations/view_ngo_requests.html', {
        'ngo': ngo, 
        'ngo_requests': ngo_requests
    })