from django.db import models

# Create your models here.
from django.utils.deconstruct import deconstructible

import uuid

    
@deconstructible
class VtronPath(object):
    

    def __call__(self, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return f'Production/test/full_body/{filename}'

@deconstructible
class OutputPath(object):

    def __call__(self, instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return f'Production/test/output/{filename}'


class APIKey(models.Model):
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name + '----' + str(self.key)
    

class VirtualTryOn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_image_url = models.ImageField(upload_to='cloth')
    full_body_image = models.ImageField(upload_to='bodyimage/')
    output_image = models.ImageField(upload_to='output/',blank=True, null=True)
    type = models.CharField(max_length=255,default="upper")
    version = models.CharField(max_length=255,default="v1")
    message_sent = models.BooleanField(default=False)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.id)