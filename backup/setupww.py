import queue
from src.config import Config
from src.camera.camera_manager import processor
from src.models import db, User
from src.camera.camera_instance import Camera
import threading
from flask import Flask
from twilio.rest import Client
from src.config import Config
from flask_login import LoginManager

notification_queue = queue.Queue()

# Flask app setup
def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = Config.DEBUG
    app.config['SECRET_KEY'] = 'a-very-secret-key' # Change this!
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = Config.SQLALCHEMY_ENGINE_OPTIONS
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprint for web auth routes
    from src.auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Blueprint for API auth routes
    from src.api.routes import api_auth as api_auth_blueprint
    app.register_blueprint(api_auth_blueprint)


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
    if not hasattr(setup_processor, "_notification_thread_started"):
        notif_thread = threading.Thread(target=notification_worker, daemon=True)
        notif_thread.start()
        setup_processor._notification_thread_started = True

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

# Twilio
def notification_worker():
    """Background thread to send WhatsApp notifications"""
    client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
    
    while True:
        try:
            item = notification_queue.get()
            if item is None:  # Poison pill to stop thread
                break
                
            camera_name, confidence = item
            message = client.messages.create(
                body=f"🚭 Smoking detected!\nCamera: {camera_name}\nConfidence: {confidence:.2f}",
                from_=Config.TWILIO_FROM_WHATSAPP,
                to=Config.TWILIO_TO_WHATSAPP
            )
            print(f"Notification sent: {message.sid}")
        except Exception as e:
            print(f"Notification error: {e}")