import cv2

max_cameras = 5 # Adjust based on your expected number of cameras
available_cameras = []

for i in range(max_cameras):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW) # Use CAP_DSHOW for DirectShow backend on Windows
    if cap.isOpened():
        available_cameras.append(i)
        cap.release()
    else:
        print(f"Camera at index {i} not found or accessible.")

print(f"Available camera indices: {available_cameras}")
