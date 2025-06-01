import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

# Create your models here.

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Accident(BaseModel):
    detected_at = models.DateTimeField(null=False, blank=False) # Get from AI result
    camera_serial = models.CharField(max_length=100, blank=False, null=False)
    confidence = models.FloatField(default=0.0)
    confirmed_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True, related_name='accidents')
    snapshot_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f'Accident {self.id} at {self.detected_at} by {self.confirmed_by.email}'


class AccidentDetail(BaseModel):
    accident = models.ForeignKey(Accident, related_name='accident_details', on_delete=models.CASCADE)
    confidence = models.FloatField(default=0.0)
    label = models.CharField(max_length=100, blank=False, null=False)
    bbox = models.CharField(max_length=100, blank=False, null=False) # Format: "x1,y1,x2,y2"

    def __str__(self):
        return f'Detail {self.id} for Accident {self.accident.id} - {self.label} with confidence {self.confidence}'
