from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

# --- Import ALL models from ALL apps ---
from users.models import CustomUser, DonorProfile, NGOProfile
from donations.models import Category, Donation, DonationOffer, NGORequest
from communications.models import Event, SuccessStory
from messaging.models import Conversation, Message

# --- Define the Custom Admin Site ---
class KindwayAdminSite(admin.AdminSite):
    site_header = "Kindway Administration"
    site_title = "Kindway Admin Portal"
    index_title = "Welcome to the Kindway Control Panel"
    
    def index(self, request, extra_context=None):
        if 'default' in request.GET:
            return super().index(request, extra_context)
        if request.user.is_authenticated and request.user.is_staff:
            return redirect(reverse('admin_dashboard'))
        return super().index(request, extra_context)

# Create the single instance
kindway_admin_site = KindwayAdminSite(name='kindway_admin')

# --- Define all ModelAdmin classes right here ---
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'submitted_at', 'is_featured')
    list_filter = ('is_featured', 'submitted_at')
    search_fields = ('name', 'city', 'story_content')
    list_editable = ('is_featured',)
    actions = ['mark_featured', 'unmark_featured']

    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_featured.short_description = "Mark selected stories as featured"

    def unmark_featured(self, request, queryset):
        queryset.update(is_featured=False)
    unmark_featured.short_description = "Unmark selected stories as featured"

class NGOProfileAdmin(admin.ModelAdmin):
    list_display = ('ngo_name', 'user_email', 'verification_status', 'view_document_link')
    list_filter = ('verification_status',)
    search_fields = ('ngo_name', 'user__email')
    filter_horizontal = ('accepted_categories',)
    actions = ['approve_ngos', 'reject_ngos']

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'

    def view_document_link(self, obj):
        if obj.document:
            return format_html('<a href="{}" target="_blank">View Document</a>', obj.document.url)
        return "No document uploaded"
    view_document_link.short_description = 'Document'
    
    def approve_ngos(self, request, queryset):
        queryset.update(verification_status='VERIFIED')
    approve_ngos.short_description = "Approve selected NGOs"

    def reject_ngos(self, request, queryset):
        queryset.update(verification_status='REJECTED')
    reject_ngos.short_description = "Reject selected NGOs"

class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    readonly_fields = ('sender', 'content', 'timestamp')

class ConversationAdmin(admin.ModelAdmin):
    list_display = ('offer', 'created_at', 'updated_at')
    inlines = [MessageInline]

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'timestamp', 'is_read')
    list_filter = ('is_read', 'conversation')

# --- Register ALL models with the custom site ---
kindway_admin_site.register(CustomUser)
kindway_admin_site.register(NGOProfile, NGOProfileAdmin)
kindway_admin_site.register(DonorProfile)

kindway_admin_site.register(Category)
kindway_admin_site.register(Donation)
kindway_admin_site.register(DonationOffer)
kindway_admin_site.register(NGORequest)

kindway_admin_site.register(Event)
kindway_admin_site.register(SuccessStory, SuccessStoryAdmin)

kindway_admin_site.register(Conversation, ConversationAdmin)
kindway_admin_site.register(Message, MessageAdmin)

# Register allauth models
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
# --- FIX 1: Import SocialAppAdmin ---
from allauth.socialaccount.admin import SocialAppAdmin 

kindway_admin_site.register(Site)
# --- FIX 2: Register SocialApp with SocialAppAdmin ---
kindway_admin_site.register(SocialApp, SocialAppAdmin) 
kindway_admin_site.register(SocialAccount)
kindway_admin_site.register(SocialToken)