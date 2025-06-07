import os
import sys
import shutil
from typing import List
import json
from fastapi import FastAPI, Request, Form, Body, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.train_utils import remove_member, retrain_model
from camera.screen import get_frame_bytes
from camera.camera_manager import camera_manager

from dotenv import load_dotenv
load_dotenv()

USERNAME = os.environ.get("LOGIN_USERNAME", "admin")
PASSWORD = os.environ.get("LOGIN_PASSWORD", "1234")

def get_members():
    try:
        with open('../data/members.json') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        with open('../data/members.json', 'w') as file:
            json.dump([], file)
        return []

def write_members(members: List):
    with open('../data/members.json', 'w') as file:
        json.dump(members, file, indent=4)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI app startup initiated. Starting CameraManager...")
    camera_manager.start()
    print("FastAPI app startup completed.")
    yield
    print("FastAPI app shutdown initiated. Stopping CameraManager...")
    camera_manager.stop()
    print("FastAPI app shutdown completed.")

app = FastAPI(lifespan=lifespan) 
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request}
    )

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username == USERNAME and password == PASSWORD:
        return RedirectResponse("/dashboard", status_code=302)
    return RedirectResponse("/", status_code=302)

@app.get("/dashboard", response_class=HTMLResponse)
def show_dashboard(request: Request, alert: str = None, tab: str = "members"):
    members = get_members()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "members": members,
        "alert": alert,
        "active_tab": tab 
    })

@app.post("/add-member")
async def add_member_api(payload: dict = Body(...)):
    new_member = payload.get("new_member")

    if not new_member:
        return JSONResponse(content={"status": "error", "message": "Member name cannot be empty."}, status_code=400)

    members = get_members()
    if new_member in members:
        return JSONResponse(content={"status": "error", "message": "Member already exists."}, status_code=400)

    members.append(new_member)
    write_members(members)
    
    member_data_path = os.path.join("..", "data", "members_data", new_member)
    os.makedirs(member_data_path, exist_ok=True)

    return JSONResponse(content={"status": "success", "message": "Member added successfully!"}, status_code=200)

@app.post("/upload-photo")
async def upload_photos(
    member: str = Form(...),
    photos: List[UploadFile] = File(...)
):
    dir_name = os.path.join("..", "data", "members_data", member)
    os.makedirs(dir_name, exist_ok=True)

    dir_files = os.listdir(dir_name)
    numbers = []
    for file in dir_files:
        name, ext = os.path.splitext(file)
        if name.isdigit():
            numbers.append(int(name))

    count = max(numbers) + 1 if numbers else 1
    files_to_train = [] 

    for photo in photos:
        contents = await photo.read()
        if not contents:
            continue

        _, ext = os.path.splitext(photo.filename)
        if not ext or ext.lower() not in ['.jpg', '.jpeg', '.png', '.bmp']:
            continue

        filename = os.path.join(dir_name, f"{count}{ext}")
        files_to_train.append(filename) 

        with open(filename, "wb") as f:
            f.write(contents)

        count += 1

    retrain_model(member, files_to_train)

    camera_manager.reload_face_encodings()

    return JSONResponse(
        content={
            "status": "success",
            "message": "Files uploaded successfully!"
        },
        status_code=200
    )


@app.post("/delete-member")
async def delete_member(member: str = Form(...)):
    dir_name = os.path.join("..", "data", "members_data", member)

    members = get_members()
    if member in members:
        members.remove(member)
        write_members(members)

    remove_member(member) 

    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)

    camera_manager.reload_face_encodings()

    return JSONResponse(
        content={"status": "success", "message": "Member deleted successfully!"},
        status_code=200
    )

@app.get("/live-camera", response_class=HTMLResponse)
async def live_camera_page(request: Request):
    return templates.TemplateResponse("live-camera.html", {"request": request})

@app.get("/video")
async def video():
    return StreamingResponse(get_frame_bytes(), media_type="multipart/x-mixed-replace; boundary=frame")