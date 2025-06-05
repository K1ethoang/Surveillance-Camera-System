from django.core.management.base import BaseCommand
from ai_app.models import CameraStream
from camera_process.utils import start_stream_camera, cleanup_dead_actors
from camera_process.registry import camera_actors
import ray

class Command(BaseCommand):
    help = 'Run YOLO on active camera streams'

    def handle(self, *args, **options):
        ray.init(include_dashboard=True)
        # cleanup_dead_actors()
        
        try:
            active_cameras = CameraStream.objects.filter(is_active=True)
            for index, cam in enumerate(active_cameras):
                start_stream_camera(cam)
        
        except Exception as e:
            self.stderr.write(f"Error occurred: {e}")
        
