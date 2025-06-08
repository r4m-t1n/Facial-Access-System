import sys
import os
import json
import face_recognition

from train_utils import get_encodings, write_encoding

member = sys.argv[1]
photos = sys.argv[2:]

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

sys.stdout.write(json.dumps(not_detected))