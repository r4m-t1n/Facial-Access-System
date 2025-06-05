import os
import sys
import pickle
import json
import subprocess
import threading


ENCODING_FILE = os.path.join(os.path.dirname(__file__), "face_encodings.pickle")

encodings_file_lock = threading.Lock()

def get_encodings(filename = ENCODING_FILE):
    with encodings_file_lock:
        if not os.path.isfile(filename):
            return {}
        
        with open(filename, "rb") as f:
            return pickle.load(f)

def get_face_encodings():
    encodings_dict = get_encodings()
    face_encodings = []
    face_names = []

    for name, encodings in encodings_dict.items():
        face_encodings.extend(encodings)
        face_names.extend([name] * len(encodings))
    return face_encodings, face_names

def write_encoding(encodings: dict):
    with encodings_file_lock:
        with open(ENCODING_FILE, "wb") as f:
            pickle.dump(encodings, f)

def remove_member(member: str):
    encodings = get_encodings()

    if member not in encodings:
        return

    del encodings[member]
    write_encoding(encodings)


def retrain_model(member, photos):
    path = os.path.join(os.path.dirname(__file__), "train_model.py")

    result = subprocess.run(
        [sys.executable, path, member] + photos,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        not_detected = json.loads(result.stdout)
    else:
        print("Error:", result.stderr)


    return not_detected
