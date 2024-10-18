from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import VirtualTryOn, APIKey
from .serializers import VirtualTryOnSerializer
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status
from .task import process_vtryon 
# from test import OOt
from django.core.files.base import ContentFile
import requests
from django.views.decorators.csrf import csrf_exempt


import logging
from django.db import OperationalError

logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['POST'])
def V2Production(request):
    cloth_image = request.FILES.get('cloth_image')
    full_body_image = request.FILES.get('model_image')
    # api_key = request.POST.get('ZENVTO_API_KEY')
    userid = request.POST.get('user_id')
    type = request.POST.get('type')
    api_key = request.headers.get('Authorization')  # Get the token from Authorization header

    if api_key is None:
        return Response({'error': 'api_key is required'}, status=status.HTTP_400_BAD_REQUEST)

    if not APIKey.objects.filter(key=api_key).exists():
        return Response({'error': 'Invalid API key'}, status=status.HTTP_401_UNAUTHORIZED)

    if cloth_image is None:
        return Response({'error': 'cloth_image is required'}, status=status.HTTP_400_BAD_REQUEST)

    if full_body_image is None:
        return Response({'error': 'full_body_image is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        vto = VirtualTryOn.objects.create(
                    product_image_url=cloth_image,
                    full_body_image=full_body_image,
                    type=type,
                    version="v2",
                    userid=userid
                )
        process_vtryon.delay(vto.id)
        return Response({'message': 'VirtualTryOn instance created.', 'id': vto.id}, status=status.HTTP_201_CREATED)
    except OperationalError as oe:
        logger.error(f"Database error occurred: {oe}", exc_info=True)
        return Response({'error': 'A database error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}", exc_info=True)
        return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def check_vton(request):
    api_key = request.headers.get('Authorization')  # Get the token from Authorization header
    vton_id = request.GET.get('id')
    if vton_id is None:
        return Response({'error': 'id is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        if not APIKey.objects.filter(key=api_key).exists():
            return Response({'error': 'api_key is required'}, status=status.HTTP_400_BAD_REQUEST)
        vton = VirtualTryOn.objects.get(id=vton_id)
        output_image = vton.output_image
        if output_image:
                serializer = VirtualTryOnSerializer(vton)
                return Response({'message': 'VirtualTryOn is Ready','data':serializer.data}, status=status.HTTP_200_OK)

        else:
                return Response({'message': 'VirtualTryOn is not Ready'}, status=status.HTTP_200_OK)
    except VirtualTryOn.DoesNotExist:
        return Response({'error': 'VirtualTryOn not Exist'}, status=status.HTTP_404_NOT_FOUND)
    
    
@api_view(['GET'])
def user_history(request,userid):
    api_key = request.headers.get('Authorization')  # Get the token from Authorization header
    try:
        if  not APIKey.objects.filter(key=api_key).exists():
            return Response({'error': 'api_key is required'}, status=status.HTTP_400_BAD_REQUEST)
        vton = VirtualTryOn.objects.filter(userid=userid)
        serializer = VirtualTryOnSerializer(vton,many=True)


        return Response({'message': 'VirtualTryOn is Ready','data':serializer.data}, status=status.HTTP_200_OK)
     
    except VirtualTryOn.DoesNotExist:
         return Response({'error': 'User not Exist'}, status=status.HTTP_404_NOT_FOUND)