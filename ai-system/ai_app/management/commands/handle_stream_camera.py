from django.core.management.base import BaseCommand
from ai_app.models import CameraStream
from camera_process.utils import start_stream_camera, cleanup_dead_actors
import ray
import time
import signal
import sys

class Command(BaseCommand):
    help = 'Run YOLO on active camera streams'

    def handle(self, *args, **options):
        # ✅ Khởi tạo Ray, có dashboard
        if not ray.is_initialized():
            ray.init(include_dashboard=True, ignore_reinit_error=True)

        self.stdout.write(self.style.SUCCESS("✅ Ray initialized. Starting camera stream processing..."))

        # ✅ Lấy danh sách camera và khởi động actor
        active_cameras = CameraStream.objects.filter(is_active=True)
        for cam in active_cameras:
            start_stream_camera(cam)

        self.stdout.write(self.style.SUCCESS(f"🎥 Started {len(active_cameras)} camera streams. Monitoring..."))

        # ✅ Setup để thoát cleanly bằng Ctrl+C
        def signal_handler(sig, frame):
            self.stdout.write("\n⛔ Exiting gracefully, shutting down Ray...")
            ray.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # ✅ Loop giữ tiến trình chạy để actor tồn tại
        try:
            while True:
                # cleanup_dead_actors()
                time.sleep(10)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error occurred: {e}"))
        finally:
            ray.shutdown()
