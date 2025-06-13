from django import forms
from .models import CameraStream

class CameraStreamForm(forms.ModelForm):
    class Meta:
        model = CameraStream
        fields = ['serial', 'location', 'stream_url', 'is_active']
