from django.shortcuts import render, redirect
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDay

from donations.models import NGORequest, DonationOffer, Category
from users.models import CustomUser, NGOProfile
from communications.models import Event
from .forms import ContactForm

def index(request):
    """
    Handles logic for the main homepage, including processing the contact form.
    """
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            name = contact_form.cleaned_data['name']
            from_email = contact_form.cleaned_data['email']
            message_body = contact_form.cleaned_data['message']
            subject = f"Contact Form Submission from {name}"
            full_message = f"You received a new message from {name} ({from_email}):\n\n{message_body}"
            admin_email = settings.DEFAULT_FROM_EMAIL
            try:
                send_mail(subject, full_message, from_email, [admin_email], fail_silently=False)
                messages.success(request, "Your message has been sent successfully! We will get back to you soon.")
                return redirect('index') 
            except Exception as e:
                messages.error(request, f"Sorry, there was an error sending your message.")
    else:
        contact_form = ContactForm()

    # --- Homepage Data Fetching ---
    ngo_requests = NGORequest.objects.filter(is_active=True).order_by('-created_at')[:3]
    donations_completed = DonationOffer.objects.filter(status='ACCEPTED').count()
    verified_ngos_count = CustomUser.objects.filter(user_type='NGO', ngoprofile__verification_status='VERIFIED').count()
    registered_donors_count = CustomUser.objects.filter(user_type='DONOR').count()
    upcoming_events = Event.objects.filter(event_date__gte=timezone.now()).order_by('event_date')[:3]
    featured_ngos = CustomUser.objects.filter(user_type='NGO', ngoprofile__verification_status='VERIFIED').order_by('?')[:3]
    
    category_icons = {
        "Food": "bi-basket3-fill", "Clothes": "bi-t-shirt", "Blood": "bi-droplet-half",
        "Books": "bi-book-half", "Toys": "bi-joystick", "Saplings": "bi-tree-fill",
        "Electronics": "bi-cpu-fill", "Furniture": "bi-lamp-fill",
    }
    all_categories = Category.objects.all()
    for cat in all_categories:
        cat.icon_class = category_icons.get(cat.name, "bi-gift-fill")

    context = {
        'contact_form': contact_form,
        'ngo_requests': ngo_requests,
        'donations_completed': donations_completed,
        'verified_ngos': verified_ngos_count,
        'registered_donors': registered_donors_count,
        'all_categories': all_categories,
        'upcoming_events': upcoming_events,
        'featured_ngos': featured_ngos,
    }
    
    return render(request, 'core/index.html', context)

def about_us(request):
    return render(request, 'core/about_us.html')

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # ... (email sending logic) ...
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact_us')
    else:
        form = ContactForm()
    return render(request, 'core/contact_us.html', {'form': form})

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('index')

    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    total_users = CustomUser.objects.count()
    new_users_last_week = CustomUser.objects.filter(date_joined__gte=seven_days_ago).count()
    total_offers = DonationOffer.objects.count()
    accepted_offers = DonationOffer.objects.filter(status='ACCEPTED').count()
    acceptance_rate = (accepted_offers / total_offers * 100) if total_offers > 0 else 0
    total_ngos = CustomUser.objects.filter(user_type='NGO').count()
    verified_ngos_count = CustomUser.objects.filter(user_type='NGO', ngoprofile__verification_status='VERIFIED').count()
    verification_rate = (verified_ngos_count / total_ngos * 100) if total_ngos > 0 else 0

    donations_by_category = (DonationOffer.objects.values('category__name').annotate(count=Count('id')).order_by('-count'))
    category_labels = [item['category__name'] for item in donations_by_category if item['category__name']]
    category_data = [item['count'] for item in donations_by_category if item['category__name']]
    
    pending_ngos_count = NGOProfile.objects.filter(verification_status='PENDING').count()
    pending_ngo_list = NGOProfile.objects.filter(verification_status='PENDING').select_related('user').order_by('-user__date_joined')[:5]
    recent_offers = DonationOffer.objects.order_by('-created_at')[:5]
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]

    context = {
        'total_users': total_users, 'new_users_last_week': new_users_last_week,
        'acceptance_rate': round(acceptance_rate, 1), 'verification_rate': round(verification_rate, 1),
        'pending_ngos': pending_ngos_count, 'pending_ngo_list': pending_ngo_list,
        'recent_offers': recent_offers, 'recent_users': recent_users,
        'category_labels': category_labels, 'category_data': category_data,
    }
    return render(request, 'core/admin_dashboard.html', context)