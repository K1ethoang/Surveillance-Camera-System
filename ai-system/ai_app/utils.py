import cv2

from datetime import datetime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from confluent_kafka import Producer
from django.conf import settings


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
    
PRODUCER_CONFIG = {
    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
    "retries": 10,  # Set the number of retries to 10
    "retry.backoff.ms": 100,  # Wait 100 milliseconds between retries
}    

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def push_to_kafka(topic,message,config=PRODUCER_CONFIG):
    producer_config = config
    try:
        producer = Producer(producer_config)
        producer.produce(topic, message, callback=delivery_report)
        producer.flush()
    except Exception as e:
        print('Push message {} with error {}'.format(message, e))
        return False
    return True