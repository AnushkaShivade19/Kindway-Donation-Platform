from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Donation
from .forms import DonationCreationForm
from users.models import CustomUser
from .models import Donation, DonationOffer, NGORequest, Category
from .forms import DirectDonationOfferForm
from geopy.distance import great_circle
from users.models import DonorProfile
@login_required
def request_donation(request, donation_id):
    # Ensure the request is a POST request for security
    if request.method != 'POST':
        return redirect('donation_list')

    donation = get_object_or_404(Donation, id=donation_id)

    # --- Security & Logic Checks ---
    # 1. Only verified NGOs can request items
    if not (request.user.user_type == 'NGO' and request.user.ngoprofile.verification_status == 'VERIFIED'):
        messages.error(request, "Only verified NGOs can request donations.")
        return redirect('donation_list')

    # 2. Ensure the donation is still available
    if donation.status != 'AVAILABLE':
        messages.error(request, "This donation is no longer available.")
        return redirect('donation_list')

    # --- Process the Request ---
    donation.requested_by = request.user
    donation.status = 'PENDING'
    donation.save(update_fields=['requested_by', 'status'])

    messages.success(request, f"You have successfully requested '{donation.title}'. The donor will be notified.")
    return redirect('dashboard')
# This new view will handle the 2-step donor process
@login_required
def offer_donation_flow(request):
    nearby_ngos = []
    # This context variable will help our template know which state to show
    context = {'state': 'initial_form'}

    if request.method == 'POST':
        form = DirectDonationOfferForm(request.POST, request.FILES)
        if form.is_valid():
            # Store item details in the session
            request.session['donation_offer_data'] = {
                'title': form.cleaned_data['title'],
                'description': form.cleaned_data['description'],
                'category_id': form.cleaned_data['category'].id,
                'delivery_type': form.cleaned_data['delivery_type'],
            }
            # Note: We won't handle the image in the session for simplicity,
            # but it can be added to the final object.

            # Get donor's coordinates from their profile
            try:
                donor_profile = request.user.donorprofile
                if not (donor_profile.latitude and donor_profile.longitude):
                    messages.error(request, "Your location is not set. Please update your profile pincode.")
                    return redirect('dashboard')
                donor_coords = (donor_profile.latitude, donor_profile.longitude)
            except donor_profile.DoesNotExist:
                messages.error(request, "Please complete your donor profile to proceed.")
                return redirect('dashboard')

            # Find relevant, nearby NGOs
            category = form.cleaned_data['category']
            relevant_ngos = CustomUser.objects.filter(
                user_type='NGO',
                ngoprofile__verification_status='VERIFIED',
                ngoprofile__accepted_categories=category,
                ngoprofile__latitude__isnull=False
            ).distinct()

            for ngo_user in relevant_ngos:
                ngo_coords = (ngo_user.ngoprofile.latitude, ngo_user.ngoprofile.longitude)
                distance = great_circle(donor_coords, ngo_coords).km
                if distance <= 50: # 50km radius
                    nearby_ngos.append({'user': ngo_user, 'distance': round(distance, 1)})
            
            nearby_ngos.sort(key=lambda x: x['distance'])

            # Update context for the template
            context['state'] = 'show_ngos'
            context['nearby_ngos'] = nearby_ngos
            context['form'] = form # Pass the form back to show the user's input

    else:
        # Initial GET request, just show a blank form
        form = DirectDonationOfferForm()

    context['form'] = form
    return render(request, 'donations/offer_donation.html', context)


# This new view handles the final step: sending the offer
@login_required
def send_offer_to_ngo(request, ngo_id):
    if request.method == 'POST' and 'donation_offer_data' in request.session:
        offer_data = request.session.pop('donation_offer_data')
        ngo = get_object_or_404(CustomUser, id=ngo_id, user_type='NGO')
        
        # Create the DonationOffer instance with all details
        DonationOffer.objects.create(
            title=offer_data['title'],
            description=offer_data['description'],
            category_id=offer_data['category_id'],
            delivery_type=offer_data['delivery_type'], # <-- Add delivery type
            donor=request.user,
            ngo=ngo,
        )
        messages.success(request, f"Your donation offer has been sent to {ngo.ngoprofile.ngo_name}!")
        return redirect('dashboard')
    
    return redirect('offer_donation_flow')

@login_required
def offer_history(request):
    """
    Displays a history of direct donation offers sent by the logged-in donor.
    """
    sent_offers = DonationOffer.objects.filter(donor=request.user).order_by('-created_at')
    
    context = {
        'sent_offers': sent_offers
    }
    return render(request, 'donations/offer_history.html', context)

from django.http import HttpResponseForbidden
@login_required
def donation_detail(request, offer_id):
    """
    Displays the details of a specific donation offer.
    """
    offer = get_object_or_404(DonationOffer, id=offer_id)

    # Security check: Only the donor who sent the offer or the NGO
    # who received it should be able to view this page.
    if request.user != offer.donor and request.user != offer.ngo:
        return HttpResponseForbidden("You do not have permission to view this page.")

    return render(request, 'donations/donation_detail.html', {'offer': offer})

@login_required
def ngo_offer_list(request):
    """
    Displays all donation offers received by the logged-in NGO.
    """
    # Security check: Ensure user is a verified NGO
    if not (request.user.user_type == 'NGO' and request.user.ngoprofile.verification_status == 'VERIFIED'):
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')

    received_offers = DonationOffer.objects.filter(ngo=request.user).order_by('-created_at')
    
    context = {
        'received_offers': received_offers
    }
    return render(request, 'donations/ngo_offer_list.html', context)


@login_required
def update_offer_status(request, offer_id, new_status):
    """
    A single view to handle both accepting and rejecting an offer.
    """
    # Security check: Ensure the request is POST for safety
    if request.method != 'POST':
        return redirect('dashboard')
    
    offer = get_object_or_404(DonationOffer, id=offer_id)

    # Security check: Ensure the logged-in user is the recipient NGO
    if request.user != offer.ngo:
        return HttpResponseForbidden("You cannot change the status of this offer.")

    # Update the status
    if new_status == 'accept':
        offer.status = 'ACCEPTED'
        messages.success(request, f"You have accepted the donation offer for '{offer.title}'.")
    elif new_status == 'reject':
        offer.status = 'REJECTED'
        messages.warning(request, f"You have rejected the donation offer for '{offer.title}'.")
    
    offer.save(update_fields=['status'])
    
    return redirect('ngo_offer_list')

from .forms import NGORequestForm

@login_required
def create_ngo_request(request):
    """
    Allows a verified NGO to post a request for a specific need.
    """
    # Security check: Ensure user is a verified NGO
    if not (request.user.user_type == 'NGO' and request.user.ngoprofile.verification_status == 'VERIFIED'):
        messages.error(request, "Only verified NGOs can post requests.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = NGORequestForm(request.POST)
        if form.is_valid():
            ngo_request = form.save(commit=False)
            ngo_request.ngo = request.user # Set the NGO to the logged-in user
            ngo_request.save()
            messages.success(request, "Your request has been posted successfully!")
            return redirect('dashboard')
    else:
        form = NGORequestForm()

    return render(request, 'donations/create_ngo_request.html', {'form': form})

from .models import NGORequest # Add NGORequest to imports if not there

@login_required
def fulfill_ngo_request(request, request_id):
    """
    Handles a donor's response to a specific NGO request.
    """
    # Get the specific need the donor wants to fulfill
    ngo_request = get_object_or_404(NGORequest, id=request_id)

    if request.method == 'POST':
        # We reuse our direct offer form
        form = DirectDonationOfferForm(request.POST, request.FILES)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.donor = request.user
            offer.ngo = ngo_request.ngo # The NGO is determined by the request
            offer.save()
            
            messages.success(request, f"Your offer has been sent to {ngo_request.ngo.ngoprofile.ngo_name} for their request!")
            return redirect('dashboard')
    else:
        # Pre-populate the form with data from the NGO's request
        initial_data = {
            'title': f"Response to: {ngo_request.title}",
            'category': ngo_request.category
        }
        form = DirectDonationOfferForm(initial=initial_data)

    context = {
        'form': form,
        'ngo_request': ngo_request
    }
    return render(request, 'donations/fulfill_request.html', context)