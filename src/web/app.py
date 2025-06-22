import os
import sys
import shutil
from typing import List
from datetime import datetime
import aiofiles
from fastapi import FastAPI, Request, Form, Body, File, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model import remove_member, retrain_model
from camera import camera_manager, get_frame_bytes
from utils import (
    MEMBERS_DATA_PATH, CAPTURED_PHOTOS,
    USERNAME, PASSWORD, SECRET_KEY,
    get_members, write_members
)

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

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/captured_photos", StaticFiles(directory=CAPTURED_PHOTOS), name="captured_photos")

async def check_user_auth(request: Request):
    if not request.session.get('is_logged_in'):
        raise HTTPException(status_code=307, detail="Not authenticated", headers={"Location": "/"})
    return request.session.get("is_logged_in")

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request, error: str = None):
    if request.session.get('is_logged_in'):
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": error}
    )

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == USERNAME and password == PASSWORD:
        request.session['is_logged_in'] = True
        return RedirectResponse("/dashboard", status_code=302)
    return RedirectResponse("/?error=1", status_code=302)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

@app.get("/dashboard", response_class=HTMLResponse, dependencies=[Depends(check_user_auth)])
def show_dashboard(request: Request, alert: str = None, tab: str = "members"):
    members = get_members()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "members": members,
        "alert": alert,
        "active_tab": tab
    })

@app.post("/add-member", dependencies=[Depends(check_user_auth)])
async def add_member_api(payload: dict = Body(...)):
    new_member = payload.get("new_member")

    if not new_member:
        return JSONResponse(content={"status": "error", "message": "Member name cannot be empty."}, status_code=400)

    members = get_members()
    if new_member.lower() in map(lambda x: x.lower(), members):
        return JSONResponse(content={"status": "error", "message": "Member already exists."}, status_code=400)

    members.append(new_member)
    write_members(members)

    member_data_path = os.path.join(MEMBERS_DATA_PATH, new_member)
    os.makedirs(member_data_path, exist_ok=True)

    return JSONResponse(content={"status": "success", "message": "Member added successfully!"}, status_code=200)

@app.post("/upload-photo", dependencies=[Depends(check_user_auth)])
async def upload_photos(
    member: str = Form(...),
    photos: List[UploadFile] = File(...)
):
    dir_name = os.path.join(MEMBERS_DATA_PATH, member)
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

@app.post("/delete-photo")
async def delete_photo(request: Request):
    data = await request.json()
    filename = data["filename"]
    file_path = os.path.join(CAPTURED_PHOTOS, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        return JSONResponse(
            content={"message": f"{filename} deleted successfully."}, status_code=200
        )
    return JSONResponse(
        content={"message": f"{filename} not found."}, status_code=404
    )

@app.post("/delete-member", dependencies=[Depends(check_user_auth)])
async def delete_member(member: str = Form(...)):
    dir_name = os.path.join(MEMBERS_DATA_PATH, member)

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

@app.get("/live-camera", response_class=HTMLResponse, dependencies=[Depends(check_user_auth)])
async def live_camera_page(request: Request):
    return templates.TemplateResponse("live-camera.html", {"request": request})

@app.get("/video", dependencies=[Depends(check_user_auth)])
async def video():
    return StreamingResponse(get_frame_bytes(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/capture", dependencies=[Depends(check_user_auth)])
async def capture_image():
    frame_bytes = camera_manager.capture_frame()

    os.makedirs(CAPTURED_PHOTOS, exist_ok=True)
    filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")

    if frame_bytes:
        filepath = os.path.join(CAPTURED_PHOTOS, filename + ".jpg")
        async with aiofiles.open(filepath, "wb") as file:
            await file.write(frame_bytes)
        return JSONResponse(content={"status": "success"}, status_code=200)
    else:
        return JSONResponse(
            content={"status": "error", "message": "Failed to capture image"},
            status_code=500
        )

@app.get("/captured-photos", dependencies=[Depends(check_user_auth)])
def get_captured_photos():
    files = os.listdir(CAPTURED_PHOTOS)
    photos = [f for f in files]
    return {"photos": photos}

@app.get("/members", dependencies=[Depends(check_user_auth)])
def members_to_js():
    return {"members": get_members()}

@app.post("/assign-photo", dependencies=[Depends(check_user_auth)])
def assign_photo(member: str = Form(...), filename: str = Form(...)):
    src_path = os.path.join(CAPTURED_PHOTOS, filename)
    dest_dir = os.path.join(MEMBERS_DATA_PATH, member)

    dest_path = os.path.join(dest_dir, filename)
    shutil.move(src_path, dest_path)

    retrain_model(member, [dest_path])
    camera_manager.reload_face_encodings()

    return JSONResponse(
        {"message": f"Photo assigned to {member}."}, status_code=200
    ) 