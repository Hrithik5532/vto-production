from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import VirtualTryOn, APIKey
import shutil
import os
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status
from .task import process_vtryon 
# from test import OOt
from django.core.files.base import ContentFile
import requests
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
@api_view(['POST'])
def V2Production(request):
    cloth_image = request.FILES.get('cloth_image')
    full_body_image = request.FILES.get('model_image')
    
    api_key = request.POST.get('ZENVTO_API_KEY')
    type = request.POST.get('type')
    
    
    
    if api_key is None:
        return Response({'error': f'api_key is required,{request.META.get}'}, status=status.HTTP_400_BAD_REQUEST)

    if not APIKey.objects.filter(key=api_key).exists():
        return Response({'error': 'Invalid API key'}, status=status.HTTP_401_UNAUTHORIZED)
        
    
    if cloth_image is None:
        return Response({'error': 'cloth_url is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if full_body_image is None:
        return Response({'error': 'full_body_image is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # # Download the cloth image
        # response = requests.get(cloth_url)
        # response.raise_for_status()  # Raise an exception for HTTP errors
        
        # # Save the image to the database
        # cloth_image_name = cloth_url.split("/")[-1]
        # cloth_image = ContentFile(response.content, cloth_image_name)
        
        # Create the VirtualTryOn instance
        vto = VirtualTryOn.objects.create(
            product_image_url=cloth_image,
            full_body_image=full_body_image,
            type=type,
            version="v2"
        )
    # Optional: Process the VTO asynchronously if needed
        process_vtryon.delay(vto.id)
        
        return Response({'message': 'VirtualTryOn instance created.', 'id': vto.id}, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        print(e)
        return Response({'error':e},status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
def check_vton(request):
    api_key = request.POST.get('ZENVTO_API_KEY')
    vton_id = request.GET.get('id')
    if vton_id is None:
        return Response({'error': 'id is required'}, status=status.HTTP_400_BAD_REQUEST)
    if api_key is None and not APIKey.objects.filter(key=api_key).exists():
        return Response({'error': 'api_key is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        vton = VirtualTryOn.objects.get(id=vton_id)
        output_image = vton.output_image
        if output_image:
            
         
            return Response({'message': 'VirtualTryOn is Ready','output_image':output_image.url}, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'VirtualTryOn is not Ready'}, status=status.HTTP_200_OK)
    except VirtualTryOn.DoesNotExist:
        return Response({'error': 'VirtualTryOn not Exist'}, status=status.HTTP_404_NOT_FOUND)