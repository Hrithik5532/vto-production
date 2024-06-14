from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='root_path'),
    
    
    path('api/v2',views.V2Production),
    # path('api/v1',V1Production)

path('api/check-vton', views.check_vton, name='check_vton'),

]
