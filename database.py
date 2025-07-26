from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DetectionLog(db.Model):
    __tablename__ = 'detection_logs'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    detail = db.Column(db.String(20), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    cam = db.Column(db.String(20))

    def __init__(self, detail, confidence, cam):
        self.detail = detail
        self.confidence = confidence
        self.cam = cam