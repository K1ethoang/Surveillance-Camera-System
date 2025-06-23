import cv2

from datetime import datetime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def save_snapshot_to_storage(frame, camera_serial: str):
    date_now = datetime.now()

    file_name = str(f'{camera_serial}/{date_now.timestamp()}')

    # Convert frame to JPEG type
    ret, jpeg = cv2.imencode('.jpg', frame)
    if not ret:
        return None

    file_content = ContentFile(jpeg.tobytes())
    file_key = f'{date_now.strftime('%Y%m%d')}/{file_name}'

    try:
        default_storage.save(file_key, file_content)
        url = default_storage.url(file_key)
        return file_key, url
    except Exception as e:
        print(f"Error saving snapshot: {e}")
        return None