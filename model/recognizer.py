import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from video.screen import detect_faces
import face_recognition

async def recognize_loop():
    async for frame in detect_faces():
        rgb_frame = frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_frame)
        print(f"{len(face_locations)} faces are found.")

asyncio.run(recognize_loop())
