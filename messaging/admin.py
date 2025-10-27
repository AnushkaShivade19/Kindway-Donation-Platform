'''
from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    """Allows viewing messages directly within the Conversation admin page."""
    model = Message
    extra = 1 # Show one extra blank message form
    readonly_fields = ('sender', 'content', 'timestamp')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('offer', 'created_at', 'updated_at')
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'timestamp', 'is_read')
    list_filter = ('is_read', 'conversation')
    '''