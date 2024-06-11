from celery import shared_task
from django.core.files.base import ContentFile
import os
import shutil
from gradio_client import Client
from django.core.exceptions import ObjectDoesNotExist
import logging
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from .models import VirtualTryOn,ShopifyStoreDetails
logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=260)
def process_vtryon(self, vton_id, isSingle):
    try:
        logger.info(f'help')
        vton = VirtualTryOn.objects.get(id=vton_id)
        model_image_path = os.path.join('/home/ubuntu/eshtyle-backend/media/', str(vton.full_body_image))
        cloth_path = os.path.join('/home/ubuntu/eshtyle-backend/media/', str(vton.product_image_url))

        # Ensure file exists before opening
        if not os.path.exists(model_image_path):
            logger.error(f'File does not exist: {model_image_path}')
            return

        logger.info(f'Starting processing vtryon with id {vton_id}')

        outfittryon = Client("yisol/IDM-VTON")

        try:
            result = outfittryon.predict(
                dict={"background": model_image_path, "layers": [model_image_path], "composite": model_image_path},
                garm_img=cloth_path,
                garment_des="Hello!!",
                is_checked=True,
                is_checked_crop=False,
                denoise_steps=30,
                seed=42,
                api_name="/tryon"
            )
        except Exception as api_error:
            logger.error(f"Error calling API: {api_error}")
            raise self.retry(exc=api_error)

        logger.info(f'Processing result !!!!!!!!!!!!!!!')
        file_path = result[0]
        with open(file_path, 'rb') as file_:
            content = file_.read()
            attr_name = f'output_image'
            getattr(vton, attr_name).save(os.path.basename(file_path), ContentFile(content), save=True)

        logger.info(f'Successfully processed vtryon with id {vton_id}')

        # Prepare the message for WebSocket
        channel_layer = get_channel_layer()
        group_name = f'vtryon_{vton_id}'
        message = {
            'type': 'chat_message',
            'message': 'Your virtual try-on images are ready!'
        }

        # Send the message
        async_to_sync(channel_layer.group_send)(group_name, message)
        logger.info(f'Sent message to group {group_name} with content: {message}')

       

    except (ObjectDoesNotExist, OSError) as e:
        logger.error(f'Error processing vtryon with id {vton_id}: {e}')
    except Exception as exc:
        logger.error(f'Retrying processing vtryon with id {vton_id} due to error: {exc}', exc_info=True)
        self.retry(exc=exc)
    finally:
        folder_path = "/tmp/gradio"
        try:
            shutil.rmtree(folder_path)
            logger.info(f"Successfully deleted temporary folder: {folder_path}")
        except OSError as e:
            logger.error(f"Error deleting temporary folder: {folder_path}. Reason: {e}")

def log_file_permissions(file_path):
    try:
        file_stat = os.stat(file_path)
        logger.info(f"File permissions for {file_path}: {oct(file_stat.st_mode)}")
        logger.info(f"File owner: UID={file_stat.st_uid}, GID={file_stat.st_gid}")
    except Exception as e:
        logger.error(f"Error getting file permissions for {file_path}: {e}")
