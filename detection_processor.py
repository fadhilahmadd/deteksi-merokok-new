import cv2
from ultralytics import YOLO
import threading
import time

class DetectionProcessor:
    def __init__(self):
        self.cameras = []
        self.model = None
        self.running = False
        self.thread = None
        self.app = None
        self.min_confidence = 0.5
        self.min_interval = 5
        
    def add_camera(self, camera):
        """Add a camera to be processed"""
        camera.app = self.app
        self.cameras.append(camera)
    
    def get_camera(self, camera_id):
        """Get camera by index"""
        if 0 <= camera_id < len(self.cameras):
            return self.cameras[camera_id]
        return None
    
    def start(self):
        if not self.running and self.cameras:
            print(f"Loading model: {self.model_path}")
            self.model = YOLO(self.model_path)
            print("Model loaded successfully")
            
            self.running = True
            for camera in self.cameras:
                camera.start(self.model, self.min_confidence, self.min_interval)
            
            self.thread = threading.Thread(target=self._monitor)
            self.thread.daemon = True
            self.thread.start()
    
    def stop(self):
        self.running = False
        for camera in self.cameras:
            camera.stop()
        if self.thread:
            self.thread.join()
    
    def _monitor(self):
        """Monitor camera threads and restart if needed"""
        while self.running:
            time.sleep(5)
            for i, camera in enumerate(self.cameras):
                if not camera.running and camera.thread and not camera.thread.is_alive():
                    print(f"Restarting camera: {camera.name}")
                    camera.start(self.model, self.min_confidence, self.min_interval)

processor = DetectionProcessor()