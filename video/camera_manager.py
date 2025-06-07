import os
import sys
import cv2
import threading
import time
from datetime import date, datetime
import numpy as np
import face_recognition

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
from model.train_utils import get_face_encodings

class CameraManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CameraManager, cls).__new__(cls)
                cls._instance.__init__()
            return cls._instance

    def __init__(self):
        self._capture: cv2.VideoCapture = None
        self._is_running: bool = False

        self._thread: threading.Thread = None

        self._current_frame_bytes: bytes = b''
        self._frame_lock = threading.Lock()

        self._known_face_encodings = []
        self._known_face_names = []

        self._log_file_path = None
        self._current_log_date = None

    def _update_log_path(self):
        today_date = date.today()
        if today_date != self._current_log_date:
            self._current_log_date = today_date

            root_pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            log_path = os.path.join(root_pth, 'data', 'logs')
            os.makedirs(log_path, exist_ok=True)

            today_filename = self._current_log_date.strftime("%d_%m_%Y.txt")
            self._log_file_path = os.path.join(log_path, today_filename)

            print(f"[CameraManager] Logging to new file: {self._log_file_path}")

    def _load_face_encodings(self):
        try:
            self._known_face_encodings, self._known_face_names = get_face_encodings()
        except Exception as e:
            print(f"[CameraManager] ERROR: Failed to load face encodings: {e}")
            self._known_face_encodings = []
            self._known_face_names = []

    def _write_log(self, name):
        self._update_log_path()

        now_timestamp = datetime.now().strftime("%H:%M:%S")
        log_text = f"[{now_timestamp}] Detected: {name}\n"
        
        try:
            with open(self._log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_text)
        except Exception as e:
            print(f"[CameraManager] ERROR: Failed to write to log file: {e}")

    def _camera_loop(self):
        self._capture = cv2.VideoCapture(0)
        if not self._capture.isOpened():
            print("[CameraManager] Failed to open camera. Camera thread will exit.")
            self._is_running = False
            return

        print("[CameraManager] Camera opened successfully. Starting frame read loop.")
        self._load_face_encodings()

        face_locations = []
        face_names = []

        while self._is_running:
            ret, frame = self._capture.read()
            if not ret:
                print("[CameraManager] ERRPR: Failed to read frame from camera. Retrying...")
                time.sleep(0.1)
                continue

            try:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    name = "Unknown"
                    if self._known_face_encodings:
                        matches = face_recognition.compare_faces(self._known_face_encodings, face_encoding, tolerance=0.5)
                        face_distances = face_recognition.face_distance(self._known_face_encodings, face_encoding)

                        if len(face_distances) > 0:
                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                name = self._known_face_names[best_match_index]

                    face_names.append(name)

                    self._write_log(name)

                for (top, right, bottom, left), name in zip(face_locations, face_names):

                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            except Exception as e:
                print(f"[CameraManager] ERROR: Face recognition failed on a frame: {e}")
                face_locations = []
                face_names = []
            
            _, buf = cv2.imencode(".jpg", frame)
            with self._frame_lock:
                self._current_frame_bytes = buf.tobytes()


        print("[CameraManager] Camera thread stopping. Releasing camera.")
        if self._capture.isOpened():
            self._capture.release()
        self._capture = None
        self._current_frame_bytes = b''
        print("[CameraManager] Camera released.")


    def start(self):
        if not self._is_running:
            print("[CameraManager] Starting camera manager.")
            self._is_running = True
            self._thread = threading.Thread(target=self._camera_loop, daemon=True)
            self._thread.start()
        else:
            print("[CameraManager] Camera manager already running.")

    def stop(self):
        if self._is_running:
            print("[CameraManager] Stopping camera manager.")
            self._is_running = False
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=5)
                if self._thread.is_alive():
                    print("[CameraManager] WARNING: Camera thread did not stop. It might be stuck.")
            self._thread = None
        else:
            print("[CameraManager] Camera manager not running.")
    
    def get_latest_frame_bytes(self) -> bytes:
        with self._frame_lock:
            return self._current_frame_bytes

    def reload_face_encodings(self):
        print("[CameraManager] Reloading face encodings triggered.")
        self._load_face_encodings()

camera_manager = CameraManager()