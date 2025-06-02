import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CameraStream(BaseModel):
    serial = models.CharField(max_length=255, blank=False, null=False)
    stream_url = models.CharField(max_length=3000, blank=False, null=False)
    location = models.CharField(max_length=255, blank=False, null=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.serial} {self.location} is {self.is_active}'
