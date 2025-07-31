## CAUTION⚠️
This is on development, not final system.

## Installation

### Environment Configuration

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```
   Or manually create a `.env` file and fill in the required values.

2. **Edit the `.env` file:**
   - Fill in your MySQL database credentials and other settings.
   - For multi-camera support, use comma-separated values for each camera property:
     - `CAMERA_SOURCES=0,1,http://x.x.x.x:xxxx/video`  *(e.g., USB camera 0, USB camera 1, and an IP camera)*
     - `CAMERA_NAMES=Camera 1,Camera 2,Camera 3`
     - `CAMERA_WIDTHS=1280,640,1920`
     - `CAMERA_HEIGHTS=720,480,1080`
     - `CAMERA_FPS=30,25,15`
   - Each value corresponds to the same camera index in all lists.

3. **For WhatsApp notifications, fill in your Twilio credentials.**
    - `TWILIO_ACCOUNT_SID:` Your Account SID from the Twilio console.
    - `TWILIO_AUTH_TOKEN`: Your Auth Token from the Twilio console.
    - `TWILIO_FROM_WHATSAPP`: Your Twilio WhatsApp-enabled number (e.g., whatsapp:+14155238886).
    - `TWILIO_TO_WHATSAPP`: The destination WhatsApp number (e.g., whatsapp:+6281234567890).

4. **Example .env configuration:**
   ```env
   CAMERA_SOURCES=0,1,http://192.168.1.10:8080/video
   CAMERA_NAMES=Front Door,Back Door,IP Cam
   CAMERA_WIDTHS=1280,1280,640
   CAMERA_HEIGHTS=720,720,480
   CAMERA_FPS=30,30,15

   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_FROM_WHATSAPP=whatsapp:+14155238886
   TWILIO_TO_WHATSAPP=whatsapp:+6281234567890
   ```

### Set Up a Virtual Environment

Create and activate a virtual environment to manage dependencies cleanly:

### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```
### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

## Install Dependencies

Install the required Python packages using:
```bash
pip install -r requirements.txt
```

## Run the Application
### On macOS/Linux:
```bash
python3 run.py
```
### On Windows:
```bash
python run.py
```

### Key Features of the System:
1. Multi-Camera Support
    - Configurable through .env file
    - Individual camera naming
    - Custom resolution and FPS per camera
2. Context-Aware Detection
    - Only logs when cigarettes are near people
    - Proximity threshold configuration
    - Reduced false positives
3. Automatic Startup
    - Detection begins immediately on app launch
    - No need to open web interface
4. WhatsApp Notifications
    - Sends real-time alerts via WhatsApp when smoking is detected.
    - Powered by Twilio for reliable delivery.
    - The notification includes the camera name and detection confidence.
5. Robust & Efficient Architecture
    - Separate threads per camera for video processing
    - Automatic camera restart on failure
    - Shared YOLO model for all cameras (memory efficient)
    - **Thread-safe logging queue:** All detection events are pushed to a single queue
    - **Single logging thread:** Only one thread writes to the database, reducing contention and improving performance with many cameras
6. Database Logging
    - MySQL integration
    - Camera-specific logging
    - Throttled logging to prevent spamming the database with repeated detections.
7. Web Interface
    - Provides real-time video feeds from all cameras.
    - Displays a log of recent detections.
    - Shows the status of each camera.

### Model
If you want try our model feel free to contact me ```zashxz011@gmail.com```