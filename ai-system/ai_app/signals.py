from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ai_app.models import CameraStream
from camera_process.utils import start_stream_camera, stop_stream_camera

@receiver(post_save, sender=CameraStream)
def handle_camera_activation(sender, instance: CameraStream, created, **kwargs):
    try:
        # Nếu là bản ghi mới được tạo
        if created:
            if instance.is_active:
                start_stream_camera(instance)
        else:
            # So sánh với bản ghi cũ
            old = CameraStream.objects.get(pk=instance.pk)
            if not old.is_active and instance.is_active:
                start_stream_camera(instance)
            elif old.is_active and not instance.is_active:
                stop_stream_camera(instance)
    except CameraStream.DoesNotExist:
        pass
    
@receiver(post_delete, sender=CameraStream)
def handle_camera_delete(sender, instance: CameraStream, **kwargs):
    stop_stream_camera(instance)