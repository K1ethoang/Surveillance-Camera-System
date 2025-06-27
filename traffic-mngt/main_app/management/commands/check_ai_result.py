import json
import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from confluent_kafka import Consumer, KafkaError

from main_app.services import MongoService
from django.conf import settings

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

CONSUMER_CONFIG = {
    'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
    'group.id': settings.KAFKA_CONSUMER_GROUP_ID,  # Consumer group ID
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
}

KAFKA_AI_TOPIC = settings.KAFKA_TOPIC


def get_ai_result():
    dt = datetime.now()
    mongo_service = MongoService()
    print('Get face result start at {}'.format(dt))
    consumer = Consumer(CONSUMER_CONFIG)
    consumer.subscribe([KAFKA_AI_TOPIC])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                print('Not message to be consume at moment')
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break
            message = json.loads(msg.value().decode('utf-8'))
            detect_at = message.get('detect_at')
            collection_name = datetime.fromtimestamp(detect_at).strftime('%Y%m%d')
            
            is_success = mongo_service.save_alert(collection_name=collection_name,message=message.copy())
            print(f'>>>>>>>>>>>> {message}')
            
            if is_success:
                print(f"save to Mongo {message}")
                consumer.commit()  # Manually commit the offset for this message
                
                async_to_sync(channel_layer.group_send)(
                    "alert_group",
                    {
                        "type": "send.alert",
                        "message": message
                    }
                )
            else:
                print(f"error to save {message}")
                
            if not message:
                continue
            
            consumer.commit()
    except KeyboardInterrupt:
        print('Consumer close...')
        consumer.commit()
        consumer.close()
    except Exception as e:
        print('Received message with error {}'.format(e))
        print('Consumer close...')
        consumer.commit()
        consumer.close()
    finally:
        print('Consumer close...')
        consumer.commit()
        consumer.close()

class Command(BaseCommand):
    help = "Check ai result"

    def handle(self, *args, **options):
        print("Start")
        get_ai_result()
            
