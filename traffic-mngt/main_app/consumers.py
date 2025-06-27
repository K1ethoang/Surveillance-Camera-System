from channels.generic.websocket import AsyncWebsocketConsumer
import json

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("alert_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("alert_group", self.channel_name)

    async def receive(self, text_data):
        # optional: xử lý nếu client gửi gì đó
        pass

    async def send_alert(self, event):
        await self.send(text_data=json.dumps(event["message"]))
