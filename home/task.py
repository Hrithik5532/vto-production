# task.py

import sys
sys.path.append('/app/vto-production')

from celery import shared_task
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
import os
import torch
from PIL import Image
import numpy as np
from diffusers.image_processor import VaeImageProcessor
from huggingface_hub import snapshot_download
from datetime import datetime
from model.cloth_masker import AutoMasker, vis_mask
from model.pipeline import ZENVTONPipeline
from utils import init_weight_dtype, resize_and_crop, resize_and_padding
import logging
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = get_task_logger(__name__)

# Define arguments
class Args:
    def __init__(self):
        self.base_model_path = "booksforcharlie/stable-diffusion-inpainting"
        self.resume_path = "zhengchong/CatVTON"
        self.output_dir = "resource/demo/output"
        self.width = 768
        self.height = 1024
        self.repaint = False
        self.allow_tf32 = True
        self.mixed_precision = "bf16"

args = Args()

def ensure_rgb(image_path):
    image = Image.open(image_path)
    if image.mode == 'RGBA':
        image = image.convert('RGB')
        image.save(image_path)
    return image_path

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5, "countdown": 5})
def process_vtryon(self, vton_id):
    from home.models import VirtualTryOn
    try:
        logger.info('Started processing vtryon task')
        vton = VirtualTryOn.objects.get(id=vton_id)
        model_image_path = os.path.join('/app/vto-production/media/', str(vton.full_body_image))
        cloth_path = os.path.join('/app/vto-production/media/', str(vton.product_image_url))

        # Ensure both images are in RGB format
        model_image_path = ensure_rgb(model_image_path)
        cloth_path = ensure_rgb(cloth_path)

        if not os.path.exists(model_image_path):
            logger.error(f'File does not exist: {model_image_path}')
            return

        # Initialize models and processors inside the task function
        repo_path = snapshot_download(repo_id=args.resume_path)

        # Pipeline
        pipeline = ZENVTONPipeline(
            base_ckpt=args.base_model_path,
            attn_ckpt=repo_path,
            attn_ckpt_version="mix",
            weight_dtype=init_weight_dtype(args.mixed_precision),
            use_tf32=args.allow_tf32,
            device='cuda'
        )

        # AutoMasker
        mask_processor = VaeImageProcessor(
            vae_scale_factor=8,
            do_normalize=False,
            do_binarize=True,
            do_convert_grayscale=True
        )
        automasker = AutoMasker(
            densepose_ckpt=os.path.join(repo_path, "DensePose"),
            schp_ckpt=os.path.join(repo_path, "SCHP"),
            device='cuda',
        )

                # Load images
        person_image = Image.open(model_image_path).convert("RGB")
        cloth_image = Image.open(cloth_path).convert("RGB")

        # Resize images
        person_image = resize_and_crop(person_image, (args.width, args.height))
        cloth_image = resize_and_padding(cloth_image, (args.width, args.height))

        # Set parameters
        cloth_type = vton.type  # or vton.cloth_type if available
        num_inference_steps = 50
        guidance_scale = 2.5
        seed = 42

        # Resize images
        person_image = resize_and_crop(person_image, (args.width, args.height))
        cloth_image = resize_and_padding(cloth_image, (args.width, args.height))

        # Generate mask
        mask = automasker(person_image, cloth_type)['mask']
        mask = mask_processor.blur(mask, blur_factor=9)

        # Set generator for seed
        generator = torch.Generator(device='cuda').manual_seed(seed) if seed != -1 else None
        
        # Run pipeline
        result_image = pipeline(
            image=person_image,
            condition_image=cloth_image,
            mask=mask,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator
        )[0]

        # Convert before saving
        if result_image.mode == "RGBA":
            result_image = result_image.convert("RGB")

        # Save result image to a path
        tmp_folder = os.path.join('/app/vto-production/', args.output_dir)
        date_str = datetime.now().strftime("%Y%m%d%H%M%S")
        result_save_path = os.path.join(tmp_folder, date_str[:8])
        if not os.path.exists(result_save_path):
            os.makedirs(result_save_path)
        result_file_path = os.path.join(result_save_path, date_str[8:] + ".png")
        result_image.save(result_file_path)

        # Save result image to the model
        with open(result_file_path, 'rb') as file_:
            content = file_.read()
            vton.output_image.save(os.path.basename(result_file_path), ContentFile(content), save=True)

        # Remove file from temp_folder
        os.remove(result_file_path)

        logger.info(f'Successfully processed vtryon with id {vton_id}')

        # Send message via channel layer
        channel_layer = get_channel_layer()
        group_name = f'vtryon_{vton_id}'
        message = {
            'type': 'chat_message',
            'message': 'Your virtual try-on image is ready!'
        }
        async_to_sync(channel_layer.group_send)(group_name, message)
        vton.message_sent = True
        vton.save()
        logger.info(f'Sent message to group {group_name} with content: {message}')

    except (ObjectDoesNotExist, OSError) as e:
        logger.error(f'Error processing vtryon with id {vton_id}: {e}')
    except Exception as exc:
        logger.error(f'Error processing vtryon with id {vton_id} due to error: {exc}', exc_info=True)
        self.retry(exc=exc)
