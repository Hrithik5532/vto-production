from django.contrib import admin

# Register your models here.
from .models import ShopifyStoreDetails,VirtualTryOn

admin.site.register(ShopifyStoreDetails)
admin.site.register(VirtualTryOn)