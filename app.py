
from flask import Flask, render_template, Response
import cv2
import time
from database import DetectionLog
from detection_processor import processor
from setup import create_app, setup_processor

app = create_app()
setup_processor(app)


@app.route('/')
def index():
    return render_template('index.html', cameras=processor.cameras)


@app.route('/detection_log')
def detection_log():
    logs = DetectionLog.query.order_by(DetectionLog.timestamp.desc()).limit(50).all()
    return render_template('log.html', logs=logs)


@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    def generate(camera_id):
        camera = processor.get_camera(camera_id)
        while True:
            frame = camera.get_latest_frame()
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                time.sleep(0.05)
    return Response(generate(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    from config import Config
    app.run(host=Config.HOST, port=Config.PORT, threaded=True, use_reloader=False)