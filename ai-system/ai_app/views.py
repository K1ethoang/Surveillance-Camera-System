# your_app/views.py
import json
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from camera_process.utils import push_to_kafka
from .models import CameraStream
from .serializers import CameraStreamSerializer
from django.views.generic import TemplateView
from .forms import CameraStreamForm
from django.conf import settings

class CameraStreamViewSet(viewsets.ModelViewSet):
    queryset = CameraStream.objects.all()
    serializer_class = CameraStreamSerializer

    @action(methods=['post'], detail=True, url_path='toggle', url_name='toggle_camera_stream')
    def toggle(self, request, pk=None):
        camera = self.get_object()
        camera.is_active = not camera.is_active
        camera.save()
        return Response(self.get_serializer(camera).data)
    

def camera_create(request):
    if request.method == 'POST':
        form = CameraStreamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('camera_list')
    else:
        form = CameraStreamForm()
    return render(request, 'camera_form.html', {'form': form, 'title': 'Add New Camera'})

def camera_update(request, pk):
    camera = get_object_or_404(CameraStream, pk=pk)
    if request.method == 'POST':
        form = CameraStreamForm(request.POST, instance=camera)
        if form.is_valid():
            form.save()
            return redirect('camera_list')
    else:
        form = CameraStreamForm(instance=camera)
    return render(request, 'camera_form.html', {'form': form, 'title': 'Edit Camera'})
    
class CameraStreamTemplateView(TemplateView):
    template_name = 'camera_stream_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cameras'] = CameraStream.objects.all()
        return context

KAFKA_TOPIC = settings.KAFKA_TOPIC
    
def send_mock_alert_view(request):
    if request.method == 'POST':
        try:
            data = {
                "camera_url": request.POST.get("camera_url"),
                "camera_serial": request.POST.get("camera_serial"),
                "detect_at": int(request.POST.get("detect_at")),
                "detections": {
                    "boxes": json.loads(request.POST.get("boxes")),
                    "scores": json.loads(request.POST.get("scores")),
                    "labels": json.loads(request.POST.get("labels"))
                }
            }
            push_to_kafka(topic=settings.KAFKA_TOPIC, message=json.dumps(data).encode('utf-8'))
            return render(request, "mock_detect.html", {
                "success": True,
                "message": f"Đã gửi cảnh báo mô phỏng thành công cho camera {data['camera_serial']}!",
            })
        except Exception as e:
            return render(request, "mock_detect.html", {
                "error": True,
                "message": f"Lỗi khi gửi dữ liệu: {str(e)}"
            })

    return render(request, "mock_detect.html")

