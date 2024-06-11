import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger(__name__)

class VTryOnConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.vton_id = self.scope['url_route']['kwargs']['vton_id']
        self.room_group_name = f'vtryon_{self.vton_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name} in group {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected: {self.channel_name} from group {self.room_group_name}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        logger.info(f"Message received: {message}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        logger.info(f"Chat message sent to WebSocket: {message}")

        await self.send(text_data=json.dumps({
            'message': message
        }))
