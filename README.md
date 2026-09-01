# Surveillance-Camera-System

> Hệ thống giám sát giao thông thời gian thực, tích hợp mô hình **YOLO11** để **phát hiện tai nạn giao thông** từ luồng camera và cảnh báo tới cơ quan giám sát.

Đây là phần **hệ thống** của đồ án tốt nghiệp *"Nghiên cứu bài toán Object Detection và phát triển hệ thống giám sát giao thông tích hợp mô hình YOLO để phát hiện tai nạn giao thông tại Việt Nam"* (Trường ĐH Giao thông Vận tải – Phân hiệu TP.HCM, 2025).

- 📄 Báo cáo: [My-Achievements / Reports / 4th-year / DATN.pdf](https://github.com/K1ethoang/My-Achievements/blob/main/Reports/4th-year/DATN.pdf)
- 🧠 Huấn luyện & đánh giá mô hình: [Accident_Detect](https://github.com/K1ethoang/Accident_Detect)

---

## Kiến trúc tổng quan

```
┌─────────────────────┐   RTMP    ┌──────────────────────┐  produce   ┌────────────┐  consume   ┌──────────────────────┐
│ camera-stream-       │ ────────▶ │ ai-system            │ ─────────▶ │  Kafka     │ ─────────▶ │ traffic-mngt         │
│ simulator            │  stream   │ (Django + Ray + YOLO)│  topic     │ ai_result  │            │ (Django + Channels)  │
│ nginx-rtmp + ffmpeg  │           │ đọc stream, detect,  │            └────────────┘            │ consumer → MongoDB   │
└─────────────────────┘           │ chụp snapshot → S3   │                                     │ + WebSocket → browser│
                                   └──────────────────────┘                                     └──────────────────────┘
```

| Thành phần | Vai trò | Công nghệ |
|---|---|---|
| **camera-stream-simulator** | Giả lập camera IP phát luồng RTMP từ file video | `tiangolo/nginx-rtmp` (Docker), `ffmpeg` |
| **ai-system** | Quản lý danh sách camera; mỗi camera active là một **Ray actor** đọc luồng RTMP, chạy YOLO11 + OpenCV; khi phát hiện tai nạn → chụp snapshot lưu S3/MinIO và **produce** kết quả vào Kafka topic `ai_result` | Django 5.2, DRF, Ray, Ultralytics YOLO11, OpenCV, `confluent-kafka`, `django-storages` (S3) |
| **traffic-mngt** | **Consume** topic `ai_result`, lưu MongoDB (mỗi ngày một collection `yyyymmdd`), đẩy realtime qua WebSocket lên giao diện; quản lý (CRUD) các bản ghi tai nạn đã xác nhận trong MySQL, xuất Excel | Django 5.2, Channels + Redis, `confluent-kafka`, `pymongo` (MongoDB), MySQL |

### Luồng dữ liệu

1. `nginx-rtmp` nhận luồng video từ camera thật hoặc từ `ffmpeg` (mô phỏng) tại `rtmp://<host>:1935/live/<key>`.
2. `ai-system` – lệnh `handle_stream_camera` khởi tạo Ray, với mỗi `CameraStream.is_active=True` sinh một `StreamProcessor` actor đọc luồng, chạy YOLO11 với ngưỡng tin cậy, phát hiện `accident` (và các đối tượng giao nhau với vùng tai nạn).
3. Khi có tai nạn: snapshot được lưu lên bucket S3/MinIO, một message JSON (`camera_url`, `camera_serial`, `snapshot_key`, `detections`, `detect_at`) được produce vào topic `ai_result`.
4. `traffic-mngt` – lệnh `check_ai_result` consume topic, ghi vào MongoDB và `group_send` tới nhóm WebSocket `alert_group`.
5. Trình duyệt mở trang *Lịch sử cảnh báo* nhận cập nhật realtime; người vận hành có thể xác nhận và lưu bản ghi tai nạn chính thức (MySQL), xuất danh sách ra Excel theo khoảng thời gian.

## Yêu cầu

- Python **3.13** (xem `.python-version`)
- Docker (chạy `nginx-rtmp`) và `ffmpeg`
- Dịch vụ hạ tầng: **Apache Kafka** (topic `ai_result`), **MySQL**, **MongoDB**, **Redis**, và **MinIO** hoặc S3
- Trọng số YOLO11 – có sẵn `ai-system/weights/yolo11_n.pt`, `yolo11_x.pt` (Git LFS)

> Trong đồ án, toàn bộ hạ tầng (Kafka, MySQL, MongoDB, RTMP server) được triển khai trên Google Compute Engine.

## Cài đặt & chạy

### 0. camera-stream-simulator (mô phỏng camera)

```bash
cd camera-stream-simulator
docker compose up -d              # nginx-rtmp lắng nghe cổng 1935
./start_cameras.sh                # ffmpeg loop videos/0420.mp4 -> rtmp://localhost/live/cam1
./stop_cameras.sh                 # dừng các tiến trình ffmpeg
```

### 1. ai-system

```bash
cd ai-system
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env               # điền SECRET_KEY, DB MySQL, KAFKA_*, MODEL_PATH_YOLO_11, AWS_* (MinIO/S3)
python manage.py migrate
python manage.py createsuperuser

python manage.py runserver 8000            # terminal 1 – web + API + Django admin
python manage.py handle_stream_camera      # terminal 2 – Ray + xử lý luồng camera
```

| Đường dẫn | Mô tả |
|---|---|
| `/` | Danh sách camera stream (thêm / sửa / bật‑tắt) |
| `/camera/create/`, `/camera/<uuid>/edit/` | Form camera |
| `/mock_detect/` | Gửi dữ liệu phát hiện tai nạn **mẫu** vào Kafka để kiểm thử |
| `/api/camera_stream/` | REST API (CRUD + `POST /api/camera_stream/<id>/toggle/`) |
| `/admin/` | Django admin |

Ray dashboard mặc định tại `http://127.0.0.1:8265` (job `handle_stream_camera`).

### 2. traffic-mngt

```bash
cd traffic-mngt
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env               # điền thêm biến MongoDB (xem bảng dưới)
python manage.py migrate
python manage.py createsuperuser

python manage.py runserver 8001            # terminal 1 – web (Daphne/ASGI, WebSocket)
python manage.py check_ai_result           # terminal 2 – Kafka consumer -> MongoDB + WebSocket
```

Biến môi trường `traffic-mngt/.env` (bổ sung ngoài `.env.sample`):

```env
DB_MONGO_HOST=127.0.0.1
DB_MONGO_PORT=27017
DB_MONGO_USER=admin
DB_MONGO_PASSWORD=...
DB_MONGO_DB=history_alert
```

| Đường dẫn | Mô tả |
|---|---|
| `/` | Trang chủ |
| `/history-alert/` | Lịch sử cảnh báo tai nạn từ hệ thống AI (realtime, dữ liệu MongoDB) |
| `/accident/` | Danh sách tai nạn đã xác nhận (MySQL) – thêm / sửa / xoá |
| `/accident/export/` | Xuất Excel theo khoảng ngày |
| `ws://<host>/ws/alerts/` | Kênh WebSocket nhận cảnh báo |

## Cấu trúc thư mục

```
Surveillance-Camera-System/
├── camera-stream-simulator/     # nginx-rtmp + script ffmpeg mô phỏng camera
│   ├── docker-compose.yml
│   ├── start_cameras.sh / stop_cameras.sh
│   └── videos/
├── ai-system/                   # Django + Ray + YOLO11 (producer)
│   ├── ai_app/                  # model CameraStream, views/API, signals, utils (Kafka + S3)
│   ├── camera_process/          # StreamProcessor (Ray actor), registry, utils
│   ├── ai_app/management/commands/handle_stream_camera.py
│   └── weights/                 # yolo11_n.pt, yolo11_x.pt
└── traffic-mngt/                # Django + Channels (consumer)
    ├── main_app/                # model Accident/User, views, MongoService, consumers (WebSocket)
    ├── main_app/management/commands/check_ai_result.py
    └── templates/
```

## Ghi chú bảo mật

`ai-system/ai_system/storage.py` và các file `.env.sample` chứa **giá trị mặc định** (SECRET_KEY, khoá S3, mật khẩu DB) chỉ dùng cho môi trường phát triển. Hãy đặt lại toàn bộ qua `.env` và **không** commit `.env` thật.

## License

Chỉ dùng cho mục đích học tập và nghiên cứu.
