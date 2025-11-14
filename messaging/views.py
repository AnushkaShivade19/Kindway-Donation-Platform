from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation

@login_required
def conversation_list(request):
    """
    Displays a list of all conversations for the logged-in user.
    """
    conversations = request.user.conversations.all().order_by('-updated_at')
    
    context = {
        'conversations': conversations
    }
    return render(request, 'messaging/conversation_list.html', context)

from .models import Message
from .forms import MessageForm # We will create this form next
# messaging/views.py

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    # --- CHANGE IS HERE ---
    # 1. Get all messages, ordered by timestamp (newest first)
    messages = conversation.messages.all().order_by('-timestamp')
    # --- END CHANGE ---

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            # On successful post, redirect to clear the form
            return redirect('conversation_detail', conversation_id=conversation.id)
    else:
        form = MessageForm()
        
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    context = {
        'conversation': conversation,
        'form': form,
        'messages': messages  # 2. Pass the ordered messages into the context
    }
    return render(request, 'messaging/conversation_detail.html', context)

# messaging/views.py
from django.http import JsonResponse
from .models import Message
import datetime

@login_required
def check_new_messages(request, conversation_id):
    # Get the timestamp of the last message the user has
    last_message_timestamp = request.GET.get('timestamp')
    
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)

    # Convert timestamp string to a datetime object
    try:
        last_message_dt = datetime.datetime.fromisoformat(last_message_timestamp)
    except (ValueError, TypeError):
        # If no timestamp, just fetch messages from the last 5 seconds
        last_message_dt = datetime.datetime.now() - datetime.timedelta(seconds=5)

    # Find messages newer than the last one, and not sent by the current user
    new_messages = conversation.messages.filter(
        timestamp__gt=last_message_dt
    ).exclude(
        sender=request.user
    ).order_by('timestamp') # Oldest-first, to append them in order

    # Format the messages for JSON
    messages_data = [
        {
            'sender_name': msg.sender.username,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime("%d %b, %H:%M")
        }
        for msg in new_messages
    ]
    
    return JsonResponse({'messages': messages_data})