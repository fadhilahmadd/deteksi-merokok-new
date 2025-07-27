import os
import cv2
import time
import numpy as np
import threading

import math
import traceback
from sqlalchemy.exc import OperationalError
from database import DetectionLog, db
import queue
from twilio.rest import Client
from config import Config

log_queue = queue.Queue()

def detection_log_worker(app):
    """Background thread to write detection logs from the queue to the database."""
    while True:
        try:
            item = log_queue.get()
            if item is None:
                break  # Poison pill to stop the thread
            class_name, confidence, cam_name = item
            with app.app_context():
                try:
                    detection = DetectionLog(
                        detail=class_name,
                        confidence=confidence,
                        cam=cam_name
                    )
                    db.session.add(detection)
                    db.session.commit()
                    print(f"{cam_name}: Logged {class_name} ({confidence:.2f}) [queue]")
                except OperationalError as e:
                    print(f"{cam_name} database error: {str(e)}")
                    db.session.rollback()
                except Exception as e:
                    print(f"{cam_name} database error: {str(e)}")
                    db.session.rollback()
        except Exception as e:
            print(f"Logging thread error: {e}")
            traceback.print_exc()


class Camera:
    def __init__(self, source, name, width=1280, height=720, fps=30, rtsp_transport='tcp'):
        self.source = source
        self.name = name
        self.width = width
        self.height = height
        self.fps = fps
        self.rtsp_transport = rtsp_transport
        self.latest_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.frame_lock = threading.Lock()
        self.running = False
        self.thread = None
        self.last_detection_time = {}
        self.model = None
        self.cap = None
        self.app = None
        self.min_confidence = 0.5
        self.min_interval = 5
        self.proximity_threshold = 0.2  # 20% of frame width
        
    def get_video_capture(self):
        """Create a new video capture object based on configuration"""
        if self.source.isdigit():
            cap = cv2.VideoCapture(int(self.source))
        elif self.source.startswith('rtsp'):
            os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = f'rtsp_transport;{self.rtsp_transport}'
            cap = cv2.VideoCapture(self.source, cv2.CAP_FFMPEG)
        else:
            cap = cv2.VideoCapture(self.source)
            
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            cap.set(cv2.CAP_PROP_FPS, self.fps)
        return cap
    
    def create_error_frame(self, message):
        """Create a placeholder frame with error message"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, message, (50, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"Camera: {self.name}", (50, 280), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame
    
    def start(self, model, min_confidence, min_interval):
        if not self.running:
            self.model = model
            self.min_confidence = min_confidence
            self.min_interval = min_interval
            
            print(f"Initializing camera: {self.name} ({self.source})")
            self.cap = self.get_video_capture()
            
            if not self.cap.isOpened():
                print(f"Error opening camera: {self.name}")
                with self.frame_lock:
                    self.latest_frame = self.create_error_frame("Camera Error")
                return False
                
            self.running = True
            self.thread = threading.Thread(target=self._process)
            self.thread.daemon = True
            self.thread.start()
            return True
        return False
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
    
    def get_latest_frame(self):
        """Get the latest annotated frame with thread safety"""
        with self.frame_lock:
            return self.latest_frame
    
    def _calculate_distance(self, box1, box2):
        """Calculate normalized distance between centers of two boxes"""
        x1_center = (box1[0] + box1[2]) / 2
        y1_center = (box1[1] + box1[3]) / 2
        x2_center = (box2[0] + box2[2]) / 2
        y2_center = (box2[1] + box2[3]) / 2
        
        distance = math.sqrt((x1_center - x2_center)**2 + (y1_center - y2_center)**2)
        max_possible = math.sqrt(self.width**2 + self.height**2)
        return distance / max_possible
    
    def _process(self):
        print(f"Starting detection on: {self.name}")
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        
        class_names = {0: 'rokok', 1: 'orang'}
        
        while self.running:
            if not self.cap.isOpened():
                if reconnect_attempts < max_reconnect_attempts:
                    print(f"{self.name}: Reconnecting...")
                    self.cap = self.get_video_capture()
                    reconnect_attempts += 1
                    time.sleep(2)
                    continue
                else:
                    print(f"{self.name}: Max reconnect attempts reached")
                    with self.frame_lock:
                        self.latest_frame = self.create_error_frame("Camera Disconnected")
                    self.running = False
                    break
            
            success, frame = self.cap.read()
            if not success:
                print(f"{self.name}: Camera read error")
                self.cap.release()
                reconnect_attempts = 0
                time.sleep(1)
                continue
            
            frame = cv2.resize(frame, (self.width, self.height))
            reconnect_attempts = 0
            
            try:
                results = self.model.track(frame, persist=True, verbose=False)
                annotated_frame = frame.copy()
                
                cigarettes = []
                persons = []
                boxes = []
                classes = []
                confidences = []
                
                if results and results[0].boxes is not None:
                    boxes = results[0].boxes.xyxy.cpu().numpy()
                    classes = results[0].boxes.cls.cpu().numpy().astype(int)
                    confidences = results[0].boxes.conf.cpu().numpy()
                    
                    for i in range(len(boxes)):
                        class_id = classes[i]
                        conf = confidences[i]
                        class_name = class_names.get(class_id, 'unknown')
                        
                        if conf >= self.min_confidence:
                            if class_name == 'rokok':
                                cigarettes.append((boxes[i], conf))
                            elif class_name == 'orang':
                                persons.append((boxes[i], conf))
                
                smoking_events = []
                for cig_box, cig_conf in cigarettes:
                    for person_box, person_conf in persons:
                        distance = self._calculate_distance(cig_box, person_box)
                        if distance < self.proximity_threshold:
                            smoking_events.append((cig_box, cig_conf))
                            break
                
                if smoking_events:
                    current_time = time.time()
                    last_time = self.last_detection_time.get(self.name, 0)
                    
                    if current_time - last_time > self.min_interval:
                        self.last_detection_time[self.name] = current_time
                        
                        highest_conf = max(smoking_events, key=lambda x: x[1])[1]
                        self._log_detection('merokok', highest_conf)
                
                for i in range(len(boxes)):
                    box = boxes[i]
                    class_id = classes[i]
                    conf = confidences[i]
                    class_name = class_names.get(class_id, 'unknown')
                    
                    x1, y1, x2, y2 = map(int, box[:4])
                    color = (0, 255, 0)
                    
                    if class_name == 'rokok':
                        is_smoking_event = any(
                            self._calculate_distance(box, person_box) < self.proximity_threshold
                            for person_box, _ in persons
                        )
                        if is_smoking_event:
                            color = (0, 0, 255)
                    
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                    label = f"{class_name} {conf:.2f}"
                    cv2.putText(annotated_frame, label, (x1, y1 - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # status indicator
                # status = f"Smoking Events: {len(smoking_events)}"
                # cv2.putText(annotated_frame, status, (10, 60), 
                #            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255) if smoking_events else (0, 255, 0), 2)
                
                with self.frame_lock:
                    self.latest_frame = annotated_frame
                
            except Exception as e:
                print(f"{self.name} detection error: {str(e)}")
                traceback.print_exc()
            
            time.sleep(1 / self.fps)
        
        if self.cap:
            self.cap.release()
        print(f"Detection stopped for {self.name}")
    
    def _log_detection(self, class_name, confidence):
        if self.app is None:
            print("App context not available. Skipping log.")
            return
            
        try:
            log_queue.put((class_name, confidence, self.name))
        except Exception as e:
            print(f"Failed to enqueue detection log: {e}")
        
        if class_name == 'merokok':
            try:
                from setup import notification_queue
                notification_queue.put((self.name, confidence))
            except Exception as e:
                print(f"Failed to enqueue notification: {e}")