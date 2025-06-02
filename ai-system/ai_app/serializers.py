from rest_framework import serializers
from .models import CameraStream

class CameraStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraStream
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
