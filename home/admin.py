from django.contrib import admin
from .models import VirtualTryOn, APIKey

# Custom admin for VirtualTryOn
class VirtualTryOnAdmin(admin.ModelAdmin):
    list_display = ('id', 'userid', 'type', 'version', 'message_sent', 'created_at')  # Columns to display
    list_filter = ('type', 'userid', 'version', 'created_at')  # Add filters for easier navigation
    search_fields = ('id', 'userid', 'type')  # Add search capability
    ordering = ('-created_at',)  # Order by the most recent entries

# Custom admin for APIKey
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'created_at')  # Columns to display
    search_fields = ('name', 'key')  # Add search capability
    ordering = ('-created_at',)  # Order by the most recent entries

# Register the models and custom admin classes
admin.site.register(VirtualTryOn, VirtualTryOnAdmin)
admin.site.register(APIKey, APIKeyAdmin)
