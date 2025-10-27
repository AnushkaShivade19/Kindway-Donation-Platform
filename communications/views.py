from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event
from .forms import EventForm # We will create this form next

@login_required
def create_event(request):
    if not (request.user.user_type == 'NGO' and request.user.ngoprofile.verification_status == 'VERIFIED'):
        messages.error(request, "Only verified NGOs can post events.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.ngo = request.user
            event.save()
            messages.success(request, "Your event has been posted successfully!")
            return redirect('dashboard')
    else:
        form = EventForm()
    return render(request, 'communications/create_event.html', {'form': form})

def event_list(request):
    events = Event.objects.order_by('event_date')
    return render(request, 'communications/event_list.html', {'events': events})

@login_required
def volunteer_for_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        # Add the current user to the volunteers list
        event.volunteers.add(request.user)
        messages.success(request, f"Thank you for volunteering for '{event.title}'!")
    return redirect('event_list') # Redirect back to the events list

from .forms import SuccessStoryForm

def submit_story(request):
    if request.method == 'POST':
        form = SuccessStoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for sharing your story! We will review it soon.")
            return redirect('index')
    else:
        form = SuccessStoryForm()
    return render(request, 'communications/submit_story.html', {'form': form})