from django.db import models
import uuid
import secrets
from django.utils.deconstruct import deconstructible

# Define custom paths for saving images based on userid and image type
@deconstructible
class BodyPath:
    def __call__(self, instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<userid>/full_body/<filename>
        return f'{instance.userid}/full_body/{filename}'

@deconstructible
class ClothPath:
    def __call__(self, instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<userid>/cloth/<filename>
        return f'{instance.userid}/cloth/{filename}'

@deconstructible
class OutputPath:
    def __call__(self, instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<userid>/output/<filename>
        return f'{instance.userid}/output/{filename}'


class APIKey(models.Model):
    # Use a CharField to store the token
    key = models.CharField(max_length=255, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + '----' + self.key

    # Override the save method to generate a token on creation
    def save(self, *args, **kwargs):
        if not self.key:  # Only generate a token if it doesn't already exist
            self.key = secrets.token_hex(32)  # Generate a secure random token
        super(APIKey, self).save(*args, **kwargs)


class VirtualTryOn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Custom upload paths based on userid
    product_image_url = models.ImageField(upload_to=ClothPath())  # Cloth image goes under user_<userid>/cloth/
    full_body_image = models.ImageField(upload_to=BodyPath())  # Body image goes under user_<userid>/full_body/
    output_image = models.ImageField(upload_to=OutputPath(), blank=True, null=True)  # Output image goes under user_<userid>/output/

    type = models.CharField(max_length=255, default="upper")
    userid = models.CharField(max_length=255, default="default")  # User identifier for folder structure
    version = models.CharField(max_length=255, default="v1")
    message_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
