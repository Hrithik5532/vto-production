from django.contrib import admin

# Register your models here.
from .models import VirtualTryOn,APIKey

admin.site.register(VirtualTryOn)
admin.site.register(APIKey)