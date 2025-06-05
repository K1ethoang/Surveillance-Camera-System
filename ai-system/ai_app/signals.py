from django.db.models.signals import pre_save
from django.dispatch import receiver
from ai_app.models import CameraStream
from camera_process.utils import start_stream_camera, stop_stream_camera

@receiver(pre_save, sender=CameraStream)
def handle_camera_activation(sender, instance: CameraStream, **kwargs):
    if instance.is_active:
        start_stream_camera(instance)
    else:
        stop_stream_camera(instance)