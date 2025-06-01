import sys
import os
import asyncio
import pickle

import numpy as np
import face_recognition

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from video.screen import get_webcam_frames

with open("face_encodings.pickle", "rb") as f:
    encodings_dict = pickle.load(f)

async def recognition_loop():
    async for frame in get_webcam_frames():
        rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            for member, members_encodings in encodings_dict.items():
                results = face_recognition.compare_faces(members_encodings, face_encoding, tolerance=0.4)

                if True in results:
                    print(f"{member} is detected!")
                    break
            else:
                print("a strange face is detected")

asyncio.run(recognition_loop())