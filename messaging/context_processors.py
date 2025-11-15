# /messaging/context_processors.py

# Import your message model
# from .models import Message  
# (You will need to uncomment and change this to your actual message model)

def unread_message_count(request):
    """
    Makes 'unread_message_count' available to all templates.
    """
    if request.user.is_authenticated:
        try:
            # --- THIS IS AN EXAMPLE ---
            # You must replace this with your project's real logic
            
            # 1. Get the count of unread messages for the logged-in user
            # count = Message.objects.filter(recipient=request.user, is_read=False).count()
            
            # 2. For now, we can just return a test number
            count = 0 # Replace this with your real query
            
            return {'unread_message_count': count}
        
        except Exception:
            # Handle errors, e.g., if the user model is not ready
            return {'unread_message_count': 0}
    
    # If no user is logged in, return 0
    return {'unread_message_count': 0}