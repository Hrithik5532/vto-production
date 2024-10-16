from django.urls import path

from . import views

urlpatterns = [
    
    
    path('api/v2', views.V2Production, name='v2_production'),
    path('api/check-vton', views.check_vton, name='check_vton'),

]
