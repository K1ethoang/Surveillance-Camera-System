import ray
from .registry import camera_actors
from .stream_processor import StreamProcessor
from django.conf import settings

def start_stream_camera(cam):
    if cam.id not in camera_actors:
        actor = StreamProcessor.remote(camera_url=cam.stream_url, camera_serial=cam.serial, model_path = settings.MODEL_PATH_YOLO_11, device_str='cpu', score_threshold=0.7)
        actor.start.remote()
        camera_actors[cam.id] = actor
        print(f"[+] Starting camera {cam.serial} - actor {actor}")

def stop_stream_camera(cam):
    if cam.id in camera_actors:
        actor = camera_actors[cam.id]
        ray.kill(actor)
        del camera_actors[cam.id]
        print(f"[-] Stopping camera {cam.serial} - actor {actor}")
        
def cleanup_dead_actors():
    to_delete = []
    for cam_id, actor in list(camera_actors.items()):
        try:
            is_alive = ray.get(actor.is_alive.remote(), timeout=2)
            if not is_alive:
                print(f"[x] Actor for cam_id {cam_id} is not alive. Removing.")
                to_delete.append(cam_id)
        except Exception as e:
            print(f"[!] Error checking actor {cam_id}: {e}")
            to_delete.append(cam_id)

    for cam_id in to_delete:
        actor = camera_actors.pop(cam_id, None)
        if actor:
            try:
                ray.kill(actor)
                print(f"[-] Actor for cam_id {cam_id} killed.")
            except Exception as e:
                print(f"[!] Error killing actor {cam_id}: {e}")        
