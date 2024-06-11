# Generated by Django 4.2.4 on 2024-06-11 04:16

from django.db import migrations, models
import home.models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VirtualTryOn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shop_id', models.CharField(blank=True, max_length=255, null=True)),
                ('product_image_url', models.CharField(max_length=255)),
                ('full_body_image', models.ImageField(upload_to=home.models.VtronPath('shop_id'))),
                ('output_image', models.ImageField(blank=True, null=True, upload_to=home.models.OutputPath('shop_id'))),
                ('version', models.CharField(default='v1', max_length=255)),
                ('message_sent', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
