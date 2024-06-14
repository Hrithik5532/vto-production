from django.db import models

# Create your models here.
from django.utils.deconstruct import deconstructible


class ShopifyStoreDetails(models.Model):
    shop_name = models.CharField(max_length=255)
    shop_url = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    shop_id = models.CharField(max_length=255)
    shop_logo = models.CharField(max_length=255,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField
    
@deconstructible
class VtronPath(object):
    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return f'Production/{instance.shop_id}/full_body/{filename}'

@deconstructible
class OutputPath(object):
    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return f'Production/{instance.shop_id}/output/{filename}'


class VirtualTryOn(models.Model):
    shop_id = models.CharField(max_length=255,blank=True, null=True)
    product_image_url = models.ImageField(upload_to='cloth')
    full_body_image = models.ImageField(upload_to=VtronPath("shop_id"))
    output_image = models.ImageField(upload_to=OutputPath("shop_id"),blank=True, null=True)
    version = models.CharField(max_length=255,default="v1")
    message_sent = models.BooleanField(default=False)
    
    
    created_at = models.DateTimeField(auto_now_add=True)