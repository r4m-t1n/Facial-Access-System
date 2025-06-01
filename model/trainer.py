import os
import pickle

import face_recognition

members_dir = os.path.join("..", "data", "members_data")
encodings_dict = {}

#not_detected = []
list_of_members = []

for folder in os.listdir(members_dir):
    if os.path.isdir(os.path.join(members_dir, folder)):
        list_of_members.append(folder)

for member_folder in list_of_members:
    member_path = os.path.join(members_dir, member_folder)
    encodings_dict[member_folder] = []

    for img_file in os.listdir(member_path):
        img_path = os.path.join(member_path, img_file)
        img = face_recognition.load_image_file(img_path)

        face_encodings = face_recognition.face_encodings(img)

        if len(face_encodings) > 0:
            encodings_dict[member_folder].append(face_encodings[0])
        else:
            pass
            #not_detected.append(img_file)

with open("face_encodings.pickle", "wb") as f:
    pickle.dump(encodings_dict, f)