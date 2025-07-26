from config import Config
from detection_processor import processor
from database import db, DetectionLog
from camera import Camera, detection_log_worker, log_queue


import threading
from flask import Flask, render_template, Response
import cv2
import time

# Flask app setup
def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = Config.DEBUG
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = Config.SQLALCHEMY_ENGINE_OPTIONS
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app

# Processor and camera setup
def setup_processor(app):
    processor.app = app
    processor.model_path = Config.MODEL_PATH
    processor.min_confidence = Config.MIN_CONFIDENCE
    processor.min_interval = Config.MIN_LOG_INTERVAL

    # Start the logging thread only once
    if not hasattr(setup_processor, "_log_thread_started"):
        log_thread = threading.Thread(target=detection_log_worker, args=(app,), daemon=True)
        log_thread.start()
        setup_processor._log_thread_started = True

    for i, source in enumerate(Config.CAMERA_SOURCES):
        name = Config.CAMERA_NAMES[i] if i < len(Config.CAMERA_NAMES) else f"Camera {i+1}"
        width = Config.CAMERA_WIDTHS[i] if i < len(Config.CAMERA_WIDTHS) else 1280
        height = Config.CAMERA_HEIGHTS[i] if i < len(Config.CAMERA_HEIGHTS) else 720
        fps = Config.CAMERA_FPS[i] if i < len(Config.CAMERA_FPS) else 15
        camera = Camera(
            source=source,
            name=name,
            width=width,
            height=height,
            fps=fps,
            rtsp_transport=Config.RTSP_TRANSPORT
        )
        processor.add_camera(camera)
    processor.start()
