from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import logging
from celery.signals import after_setup_logger, after_setup_task_logger

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZenVton_django_app.settings')

app = Celery('ZenVton_django_app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery configuration
app.conf.broker_connection_retry = True
app.conf.broker_connection_retry_on_startup = True

# Setup logging
@after_setup_logger.connect
def setup_celery_logger(logger, *args, **kwargs):
    handler = logging.FileHandler('celery.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

@after_setup_task_logger.connect
def setup_celery_task_logger(logger, *args, **kwargs):
    handler = logging.FileHandler('celery_task.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
