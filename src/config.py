import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))

    # MySQL configuration
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Detection processor
    MODEL_PATH = os.getenv('MODEL_PATH', 'best.pt')
    MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', 0.5))
    MIN_LOG_INTERVAL = float(os.getenv('MIN_LOG_INTERVAL', 5))
    PROXIMITY_THRESHOLD = float(os.getenv('PROXIMITY_THRESHOLD', 0.3))

    # Multi-camera
    CAMERA_SOURCES = os.getenv('CAMERA_SOURCES', '0').split(',')
    CAMERA_NAMES = os.getenv('CAMERA_NAMES', 'Camera 1').split(',')
    CAMERA_WIDTHS = list(map(int, os.getenv('CAMERA_WIDTHS', '1280').split(',')))
    CAMERA_HEIGHTS = list(map(int, os.getenv('CAMERA_HEIGHTS', '720').split(',')))
    CAMERA_FPS = list(map(int, os.getenv('CAMERA_FPS', '30').split(',')))
    RTSP_TRANSPORT = os.getenv('RTSP_TRANSPORT', 'tcp')
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_FROM_WHATSAPP = os.getenv('TWILIO_FROM_WHATSAPP')
    TWILIO_TO_WHATSAPP = os.getenv('TWILIO_TO_WHATSAPP')