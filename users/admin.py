# users/admin.py
'''
from django.contrib import admin
from django.utils.html import format_html
from .models import CustomUser, NGOProfile, DonorProfile
from kindway.admin import kindway_admin_site

class NGOProfileAdmin(admin.ModelAdmin):
    list_display = ('ngo_name', 'user_email', 'verification_status', 'view_document_link')
    list_filter = ('verification_status',)
    search_fields = ('ngo_name', 'user__email')
    filter_horizontal = ('accepted_categories',)
    # Add actions to approve/reject
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
        self.message_user(request, f"{queryset.count()} NGO(s) have been verified.")
    approve_ngos.short_description = "Approve selected NGOs"

    def reject_ngos(self, request, queryset):
        queryset.update(verification_status='REJECTED')
        self.message_user(request, f"{queryset.count()} NGO(s) have been rejected.")
    reject_ngos.short_description = "Reject selected NGOs"

# Register your models

admin.site.register(CustomUser)
admin.site.register(NGOProfile, NGOProfileAdmin)
admin.site.register(DonorProfile)
'''
