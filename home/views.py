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
from .task import process_vtryon 
# from test import OOt
from django.core.files.base import ContentFile
import requests

# @shop_login_required
def index(request):

    clientId = request.GET.get('clientId')
    customerID = request.GET.get('customerID',"testuser")
    try:
        ssd = ShopifyStoreDetails.objects.get(shop_id=clientId)

    
        access_token = ShopifyStoreDetails.objects.get(shop_id=clientId).access_token
    
        url = "https://trizyn.com/api/tryon/init"
        body={
            "accessToken":access_token,
            "customerID":customerID
        }
        response= requests.post(url,json=body)
        if response.json()['message']=="Authorize Successfull":
            shop_status = "authorized"
        else:
            shop_status = "authorized"

        product_image_url = str(ssd.file_path) +str(request.GET.get('product_image_url'))
        shop_link = ssd.shop_url
        shop_logo = ssd.shop_logo
            
        shop_name = ssd.shop_name
        return render(request, 'home/vto.html', {'shop_status':shop_status,'product_image_url':product_image_url,"shop_id":ssd.shop_id,'shop_link':shop_link,'shop_name':shop_name,'shop_logo':shop_logo})

        
    except Exception as e:
        print(e)
        return render(request, '500.html')
    
  











@api_view(['POST'])
def V2Production(request):
    cloth_url = request.POST.get('cloth')
    full_body_image = request.FILES.get('model_image')
    shop_id = request.data.get('shop_id')
    
    
    print(cloth_url,full_body_image)
    
    if shop_id is None:
        return Response({'error': 'shop_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if cloth_url is None:
        return Response({'error': 'cloth_url is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if full_body_image is None:
        return Response({'error': 'full_body_image is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Download the cloth image
        response = requests.get(cloth_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Save the image to the database
        cloth_image_name = cloth_url.split("/")[-1]
        cloth_image = ContentFile(response.content, cloth_image_name)
        
        # Create the VirtualTryOn instance
        vto = VirtualTryOn.objects.create(
            shop_id=shop_id,
            product_image_url=cloth_image,
            full_body_image=full_body_image,
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
    vton_id = request.GET.get('id')
    if vton_id is None:
        return Response({'error': 'id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        vton = VirtualTryOn.objects.get(id=vton_id)
        output_image = vton.output_image
        if output_image:
            
            # try:
            #     url ="https://trizyn.com/api/tryon/updateUsage"
            #     body ={
            #         "accessToken": ShopifyStoreDetails.objects.get(shop_id=vton.shop_id).access_token,
            #         "customerID":"testuser",
            #         "tryonImage":output_image.url
            #     }
            #     response = requests.post(url,json=body)
            #     # if response.status_code == 200:
            #     # else:
            #     return Response({'message': 'VirtualTryOn is Ready','output_image':output_image.url}, status=status.HTTP_200_OK)
            #         # return Response({'message': "Something Went Wrong"}, status=status.HTTP_200_OK)
            # except:
                return Response({'message': 'VirtualTryOn is Ready','output_image':output_image.url}, status=status.HTTP_200_OK)

            
            
        else:
            return Response({'message': 'VirtualTryOn is not Ready'}, status=status.HTTP_200_OK)
    except VirtualTryOn.DoesNotExist:
        return Response({'error': 'VirtualTryOn not Exist'}, status=status.HTTP_404_NOT_FOUND)