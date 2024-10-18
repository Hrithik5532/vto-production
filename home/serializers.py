from rest_framework import serializers
from .models import *


class VirtualTryOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualTryOn
        fields = '__all__'
        
