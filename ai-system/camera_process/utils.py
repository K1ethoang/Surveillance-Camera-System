import ray
from .registry import camera_actors
from .stream_processor import StreamProcessor

def start_stream_camera(cam):
    if cam.id not in camera_actors:
        actor = StreamProcessor.remote(camera_url=cam.stream_url, camera_serial=cam.serial, device_str='cpu')
        actor.start.remote()
        camera_actors[cam.id] = actor
        print(f"[+] Starting camera {cam.serial} - actor {actor}")

def stop_stream_camera(cam):
    if cam.id in camera_actors:
        actor = camera_actors[cam.id]
        actor.stop.remote()
        del camera_actors[cam.id]
        print(f"[-] Stopping camera {cam.serial} - actor {actor}")
        
def cleanup_dead_actors():
    to_delete = []
    for cam_id, actor in camera_actors.items():
        try:
            if not ray.get(actor.is_alive.remote()):
                print(f"[x] Actor for cam_id {cam_id} is dead. Removing.")
                to_delete.append(cam_id)
        except Exception as e:
            print(f"[!] Failed to check actor {cam_id}: {e}")
            to_delete.append(cam_id)

    for cam_id in to_delete:
        actor = camera_actors.get(cam_id)
        if actor:
            # Không cần gọi actor.stop.remote() vì actor chết rồi
            del camera_actors[cam_id]
        
