import os
import json
from typing import List

from dotenv import load_dotenv
load_dotenv()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))

DATA_DIR = os.path.join(ROOT_DIR, 'data')
MEMBERS_JSON_PATH = os.path.join(DATA_DIR, 'members.json')
MEMBERS_DATA_PATH = os.path.join(DATA_DIR, 'members_data')

CAPTURED_PHOTOS = os.path.join(ROOT_DIR, "captured_photos")

USERNAME = os.environ.get("LOGIN_USERNAME", "admin")
PASSWORD = os.environ.get("LOGIN_PASSWORD", "1234")
SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_key_or_be_hacked")

def get_members():
    try:
        os.makedirs(os.path.dirname(MEMBERS_JSON_PATH), exist_ok=True)
        with open(MEMBERS_JSON_PATH, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        with open(MEMBERS_JSON_PATH, 'w') as file:
            json.dump([], file)
        return []

def write_members(members: List):
    with open(MEMBERS_JSON_PATH, 'w') as file:
        json.dump(members, file, indent=4)