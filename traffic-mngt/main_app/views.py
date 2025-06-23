import datetime
import os
import uuid
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from main_app.forms import AccidentForm
from django.core.files.base import ContentFile
from main_app.models import Accident
from main_app.serializers import AccidentSerializer
from main_app.services import MongoService

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
def history_alert_view(request):
    service = MongoService()
    alerts = service.get_latest_alerts(limit_days=5)

    for alert in alerts:
        # Convert detect_at timestamp -> readable
        if "detect_at" in alert:
            try:
                alert["detect_at"] = datetime.datetime.fromtimestamp(alert["detect_at"]).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                alert["detect_at"] = str(alert["detect_at"])

    paginator = Paginator(alerts, 10)
    page = request.GET.get('page')
    alerts_page = paginator.get_page(page)
    
    return render(request, 'history_alert.html', {'alerts': alerts_page})


def accident_list_view(request):
    accident_qs = Accident.objects.all().order_by('-created_at')
    paginator = Paginator(accident_qs, 10)  # 10 tai nạn mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'accident/accident_list.html', {
        'accidents': page_obj
    })


def accident_detail(request, pk):
    accident = get_object_or_404(Accident, pk=pk)
    return render(request, 'accident/accident_detail.html', {'accident': accident})


def accident_create(request):
    if request.method == 'POST':
        if 'snapshot' in request.FILES:
            original_file = request.FILES['snapshot']
            ext = os.path.splitext(original_file.name)[1] or '.jpg'
            new_filename = f"{request.POST.get('camera_serial', 'camera')}_{uuid.uuid4()}{ext}"

            # Tạo lại file với tên mới
            new_file = ContentFile(original_file.read())
            new_file.name = new_filename
            request.FILES['snapshot'] = new_file

        form = AccidentForm(request.POST, request.FILES)
        if form.is_valid():
            accident = form.save(commit=False)
            accident.confirmed_by = request.user
            accident.save()
            return redirect('accident')
    else:
        form = AccidentForm()
    return render(request, 'accident/accident_form.html', {'form': form, 'is_create': True})


def accident_update(request, pk):
    accident = get_object_or_404(Accident, pk=pk)
    old_snapshot = accident.snapshot if accident.snapshot else None

    if request.method == 'POST':
        if 'snapshot' in request.FILES:
            # Xoá ảnh cũ trên S3 (nếu có)
            if old_snapshot:
                old_snapshot.delete()

            # Đổi tên file mới trước khi gán vào form
            original_file = request.FILES['snapshot']
            ext = os.path.splitext(original_file.name)[1] or '.jpg'
            new_filename = f"{accident.camera_serial}_{uuid.uuid4()}{ext}"
            new_file = ContentFile(original_file.read())
            new_file.name = new_filename
            request.FILES['snapshot'] = new_file

        form = AccidentForm(request.POST, request.FILES, instance=accident)
        if form.is_valid():
            accident = form.save(commit=False)
            accident.confirmed_by = request.user
            accident.save()
            return redirect('accident')
    else:
        form = AccidentForm(instance=accident)

    return render(request, 'accident/accident_form.html', {'form': form})


def accident_delete(request, pk):
    accident = get_object_or_404(Accident, pk=pk)
    if request.method == 'POST':
        accident.delete()
        return redirect('accident')
    return render(request, 'accident/accident_confirm_delete.html', {'accident': accident})