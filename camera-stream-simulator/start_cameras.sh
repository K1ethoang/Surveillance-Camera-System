#!/bin/bash

# ✅ Cấu hình đường dẫn RTMP (không có dấu / ở cuối)
RTMP_PATH="rtmp://localhost/live"

# ✅ Kiểm tra ffmpeg đã được cài
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg chưa được cài đặt. Vui lòng cài ffmpeg trước khi chạy script."
    exit 1
fi

# ✅ Đường dẫn video
VIDEO1="./videos/0420.mp4"
VIDEO2="./videos/0420.mp4"

# ✅ Kiểm tra file video có tồn tại
if [[ ! -f "$VIDEO1" ]]; then
    echo "❌ File video $VIDEO1 không tồn tại!"
    exit 1
fi

if [[ ! -f "$VIDEO2" ]]; then
    echo "❌ File video $VIDEO2 không tồn tại!"
    exit 1
fi

# ✅ Tên stream key
KEY1="cam1"
KEY2="cam2"

# ✅ Địa chỉ RTMP
URL1="$RTMP_PATH/$KEY1"
URL2="$RTMP_PATH/$KEY2"

# ✅ Chạy ffmpeg nền, ẩn toàn bộ output
ffmpeg -re -stream_loop -1 -i "$VIDEO1" -c:v libx264 -f flv "$URL1" >/dev/null 2>&1 &
# ffmpeg -re -stream_loop -1 -i "$VIDEO2" -c:v libx264 -f flv "$URL2" >/dev/null 2>&1 &

# ✅ In thông tin
echo "🎥 Đang stream camera:"
echo "🔗 Camera 1: $URL1"
# echo "🔗 Camera 2: $URL2"
