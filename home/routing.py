from django.urls import path
from . import consumer

websocket_urlpatterns = [
    path('ws/vtryon/<uuid:vton_id>/', consumer.VTryOnConsumer.as_asgi()),
]
