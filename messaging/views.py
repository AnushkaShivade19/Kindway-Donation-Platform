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

@login_required
def conversation_detail(request, conversation_id):
    """
    Displays messages in a conversation and handles sending new messages.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            return redirect('conversation_detail', conversation_id=conversation.id)
    else:
        form = MessageForm()
        
    # Mark messages as read
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    context = {
        'conversation': conversation,
        'form': form
    }
    return render(request, 'messaging/conversation_detail.html', context)