#!/bin/bash

echo "🔍 Đang tìm và dừng các tiến trình ffmpeg..."

# Tìm tất cả tiến trình ffmpeg đang stream tới RTMP (có rtmp:// trong command line)
PIDS=$(ps aux | grep '[f]fmpeg.*rtmp://' | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "✅ Không có tiến trình ffmpeg nào đang chạy."
    exit 0
fi

# Dừng các tiến trình đó
echo "🛑 Đang dừng các tiến trình ffmpeg: $PIDS"
kill $PIDS

echo "✅ Đã dừng tất cả camera stream."
