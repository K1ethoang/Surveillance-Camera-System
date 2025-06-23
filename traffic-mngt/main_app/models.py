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
    camera_serial = models.CharField(max_length=100, blank=False, null=False)
    confirmed_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True, related_name='accidents')
    snapshot = models.ImageField(upload_to='accidents/snapshots/')

    def __str__(self):
        return f'Accident {self.id} created at {self.created_at} by {self.confirmed_by.email}'
