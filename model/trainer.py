import os
import pickle

import face_recognition

ENCODING_FILE = os.path.join(os.path.dirname(__file__), "face_encodings.pickle")

def get_encodings(filename = ENCODING_FILE):
    if not os.path.isfile(filename):
        return {}
    
    with open(filename, "rb") as f:
        return pickle.load(f)

def write_encoding(encodings: dict):
    with open(ENCODING_FILE, "wb") as f:
        pickle.dump(encodings, f)

def remove_member(member: str):
    encodings = get_encodings()

    if member not in encodings:
        return

    del encodings[member]
    write_encoding(encodings)


def train_member(member: str, photos: list):
    not_detected = []

    encodings_dict = get_encodings()
    
    if member not in encodings_dict:
        encodings_dict[member] = []

    for img_path in photos:
        img = face_recognition.load_image_file(img_path)

        face_encodings = face_recognition.face_encodings(img)

        if len(face_encodings) > 0:
            encodings_dict[member].append(face_encodings[0])
        else:
            not_detected.append(os.path.basename(img_path))
    
    write_encoding(encodings_dict)

    return not_detected