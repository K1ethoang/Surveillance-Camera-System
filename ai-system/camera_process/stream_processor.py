import datetime
import json
import ray
import torch
import cv2
import time
import sys
import os
from typing import Dict, List, Optional
from ultralytics import YOLO
from ai_app.utils import push_to_kafka, save_snapshot_to_storage
from django.conf import settings


# Global variables
CLASSES = ['accident', 'bicycle', 'bus', 'car', 'motorcycle', 'person', 'truck']


def load_model(model_path: str, device: torch.device) -> object:
    print(f"Loading model from {model_path} on {device}...")
    model = YOLO(model_path)
    # Set the device
    model.to(device)
    print(f"Model loaded successfully on {device}.")
    return model


def boxes_intersect(box1: List[float], box2: List[float]) -> bool:
    """
    Check if two bounding boxes intersect

    Args:
        box1: First box in [x1, y1, x2, y2] format
        box2: Second box in [x1, y1, x2, y2] format

    Returns:
        True if boxes intersect, False otherwise
    """
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2

    return not (x2_1 < x1_2 or x1_1 > x2_2 or y2_1 < y1_2 or y1_1 > y2_2)


def process_results(results, classes: List[str]) -> Dict:
    boxes, scores, labels = [], [], []
    result = results[0]
    if hasattr(result, 'boxes'):
        for box in result.boxes:
            xyxy = box.xyxy.cpu().numpy()[0]
            boxes.append(xyxy)
            scores.append(box.conf.cpu().numpy()[0])
            labels.append(int(box.cls.cpu().numpy()[0]))
    return {
        'boxes': boxes,
        'scores': scores,
        'labels': labels
    }


def draw_detections(
    frame,
    boxes: List[List[float]],
    scores: List[float],
    labels: List[int],
    class_names: List[str],
    count_display: bool = False,
    frame_width: Optional[int] = None
) -> Dict:
    """
    Vẽ các bounding boxes của accident (màu đỏ) và các object liên quan (màu xanh) nếu đườc phát hiện 
    giao nhau với accident. Đồng thời cập nhật số lượng đối tượng.

    Returns:
        object_counts dict
    """
    object_counts = {class_name: 0 for class_name in class_names}
    accident_indices = [i for i, label in enumerate(labels) if class_names[label] == 'accident']
    accident_boxes = [boxes[i] for i in accident_indices]
    object_counts["accident"] = len(accident_indices)

    # Vẽ accident boxes (màu đỏ)
    for i in accident_indices:
        box = boxes[i]
        score = scores[i]
        xmin, ymin, xmax, ymax = map(int, box)
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 255), 3)
        cv2.putText(
            frame,
            f"accident: {score:.2f}",
            (xmin, ymin - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    # Vẽ các object giao cắt với accident boxes (màu xanh)
    if accident_boxes:
        for i in range(len(boxes)):
            if i in accident_indices:
                continue
            box = boxes[i]
            label_idx = labels[i]
            score = scores[i]
            class_name = class_names[label_idx]
            if any(boxes_intersect(box, acc_box) for acc_box in accident_boxes):
                xmin, ymin, xmax, ymax = map(int, box)
                object_counts[class_name] += 1
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"{class_name}: {score:.2f}",
                    (xmin, ymin - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

    # Nếu yêu cầu hiển thị counts trên frame (chỉ dùng trong detect_on_video)
    if count_display and frame_width:
        margin = 10
        y_offset = margin
        for class_name, count in object_counts.items():
            if count > 0:
                text = f"{class_name}: {count}"
                (text_width, text_height), _ = cv2.getTextSize(
                    text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2
                )
                cv2.rectangle(
                    frame,
                    (int(frame_width - text_width - margin*2 - 50), int(y_offset + 50)),
                    (int(frame_width - margin - 50), int(y_offset + text_height + margin + 50)),
                    (255, 255, 255),
                    -1
                )
                cv2.putText(
                    frame,
                    text,
                    (int(frame_width - text_width - margin*1.5 - 50), int(y_offset + text_height + 50)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 0),
                    2
                )
                y_offset += text_height + margin*1.5

    return object_counts


def detect_on_video(
    model: object,
    video_path: str,
    device: torch.device,
    score_threshold: float = 0.2,
    is_snapshot: bool = True,
) -> None:
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_count = 0
    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 10 == 0:
            elapsed = time.time() - start_time
            fps_processing = frame_count / elapsed
            print(f"Processing frame {frame_count}/{total_frames} ({fps_processing:.2f} FPS)")

        results = model(frame, conf=score_threshold)
        detections = process_results(results, CLASSES)
        boxes = detections['boxes']
        scores = detections['scores']
        labels = detections['labels']

        # Vẽ detections và cập nhật object_counts
        object_counts = draw_detections(
            frame,
            boxes,
            scores,
            labels,
            CLASSES,
            count_display=True,
            frame_width=width
        )

        # Snapshot: lưu ảnh nếu được yêu cầu
        if is_snapshot:
            snapshot_url = save_snapshot_to_storage(frame=frame, camera_serial=123)

    cap.release()


KAFKA_TOPIC = settings.KAFKA_TOPIC

@ray.remote
class StreamProcessor:
    def __init__(self, camera_url, camera_serial, model_path, device_str='cpu', score_threshold=0.6, verbose=False):
        self.camera_url = camera_url
        self.camera_serial = camera_serial
        self.device = torch.device(device_str)
        self.model_path = model_path
        self.score_threshold = score_threshold
        self.running = False
        self.model = load_model(self.model_path, self.device)
        self.verbose = verbose
        
    def __del__(self):
        try:
            self.stop()
        except:
            pass
        
    def is_alive(self):
        return self.running

    def start(self):
        self.running = True
        print(f"[+] Starting processing for {self.camera_url}")
        n_frame_to_pass = 5

        while self.running:
            try:
                cap = cv2.VideoCapture(self.camera_url)
                if not cap.isOpened():
                    print(f"[!] Failed to open stream: {self.camera_url}. Retrying in 5s...")
                    cap.release()
                    time.sleep(5)
                    continue

                frame_count = 0
                start_time = time.time()

                while self.running:
                    ret, frame = cap.read()
                    if not ret:
                        print(f"[!] Failed to read frame from {self.camera_url}. Reconnecting in 5s...")
                        break  # Reconnect outer loop

                    # frame_count += 1
                    # if frame_count % n_frame_to_pass != 0:
                    #     continue
                    
                    if frame_count % 10 == 0:
                        elapsed = time.time() - start_time
                        fps_processing = frame_count / elapsed
                        print(f"[{self.camera_url}] Processing frame {frame_count} ({fps_processing:.2f} FPS)")

                    results = self.model(frame, conf=self.score_threshold, verbose=self.verbose)
                    detections = process_results(results, CLASSES)
                    boxes = detections['boxes']
                    scores = detections['scores']
                    labels = detections['labels']

                    draw_detections(
                        frame,
                        boxes,
                        scores,
                        labels,
                        CLASSES,
                        count_display=False
                    )

                    accident_indices = [i for i, label in enumerate(labels) if CLASSES[label] == 'accident']
                    if len(accident_indices) > 0:
                        snapshot_key, image_url = save_snapshot_to_storage(frame=frame, camera_serial=self.camera_serial)
                        
                        detections_clean = {
                            'boxes': [box.tolist() for box in detections['boxes']],
                            'scores': [float(score) for score in detections['scores']],
                            'labels': [CLASSES[label] for label in detections['labels']],
                        }
                        
                        message = {
                            'camera_url': self.camera_url,
                            'camera_serial': self.camera_serial,
                            'snapshot_key': snapshot_key,
                            'detections': detections_clean,
                            'detect_at': int(datetime.datetime.now().timestamp()),
                        }
                        result = push_to_kafka(topic=KAFKA_TOPIC,message=json.dumps(message).encode('utf-8'))
                        print(result)
                    
                    time.sleep(0.2)  # Giảm tải CPU

                cap.release()
                print(f"[!] Released video capture for {self.camera_url}, will retry...")

            except Exception as e:
                print(f"[!] Exception occurred in stream {self.camera_url}: {e}", file=sys.stderr)
                time.sleep(5)
                
        cap.release()
        
    def stop(self):
        self.running = False
