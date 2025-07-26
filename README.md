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

3. **Example .env configuration:**
   ```env
   CAMERA_SOURCES=0,1,http://192.168.1.10:8080/video
   CAMERA_NAMES=Front Door,Back Door,IP Cam
   CAMERA_WIDTHS=1280,1280,640
   CAMERA_HEIGHTS=720,720,480
   CAMERA_FPS=30,30,15
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
python3 app.py
```
### On Windows:
```bash
python app.py
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
4. Robust & Efficient Architecture
    - Separate threads per camera for video processing
    - Automatic camera restart on failure
    - Shared YOLO model for all cameras (memory efficient)
    - **Thread-safe logging queue:** All detection events are pushed to a single queue
    - **Single logging thread:** Only one thread writes to the database, reducing contention and improving performance with many cameras
5. Database Logging
    - MySQL integration
    - Camera-specific logging
    - Throttled logging to prevent spam
6. Web Interface
    - Real-time camera feeds
    - Detection log display
    - Camera status indicators