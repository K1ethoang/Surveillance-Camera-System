# your_app/views.py
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CameraStream
from .serializers import CameraStreamSerializer
from django.views.generic import TemplateView
from .forms import CameraStreamForm

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
