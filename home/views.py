from django.shortcuts import render
import shopify
from shopify_app.decorators import shop_login_required
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import VirtualTryOn,ShopifyStoreDetails
import shutil
import os
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status
# @shop_login_required
def index(request):

    clientId = request.GET.get('client_id')
    ssd = ShopifyStoreDetails.objects.get(shop_id=clientId)
    product_image_url =ssd.file_path + str(request.GET.get('product_image_url'))
    product_url = request.GET.get('product_url')
    # access_token = ShopifyStoreDetails.objects.get(shop_id=clientId).access_token
    
    return render(request, 'home/vto.html', {'product_image_url':product_image_url})


@api_view(['POST'])
def V2Production(request):
    cloth_image = request.POST.get('cloth')
    full_body_image = request.FILES.get('model_image')
    shop_id = request.data.get('shop_id')
    
    if shop_id is None:
        return Response({'error':'shop_id is required'},status=status.HTTP_400_BAD_REQUEST)
    
    if cloth_image is None:
        return Response({'error':'cloth_image is required'},status=status.HTTP_400_BAD_REQUEST)
    
    if full_body_image is None:
        return Response({'error':'full_body_image is required'},status=status.HTTP_400_BAD_REQUEST)
    
    vto = VirtualTryOn.objects.create(shop_id=shop_id,product_image_url=cloth_image,full_body_image=full_body_image,version="v2")
    vto.save()
    
    return Response({'message': 'Your request is being processed. If our system is experiencing high demand, you will be placed in a queue. Dont worry, we will email you once your virtual try-on is ready.','id':vto.id}, status=status.HTTP_202_ACCEPTED)
    
    