import os
import shutil
from typing import List
import json
from fastapi import FastAPI, Request, Form, Body, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.environ.get("LOGIN_USERNAME", "admin")
PASSWORD = os.environ.get("LOGIN_PASSWORD", "1234")

def get_members():
    with open('../data/members.json') as file:
        data = json.load(file)

    return data

def write_members(members: List):
    with open('../data/members.json', 'w') as file:
        json.dump(members, file, indent=4)

app = FastAPI()
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
def dashboard(request: Request):
    members = get_members()
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "members": members}
    )

@app.post("/add-member")
async def add_member_api(request: Request, payload: dict = Body(...)):
    new_member = payload.get("new_member")

    if not new_member:
        return JSONResponse(content={"status": "error"}, status_code=400)

    members = get_members()
    if new_member in members:
        return JSONResponse(content={"status": "error"}, status_code=400)

    members.append(new_member)
    write_members(members)
    
    os.makedirs(
        os.path.join("..", "data", "members_data", new_member), exist_ok=True
    )

    return JSONResponse(content={"status": "success"}, status_code=200)

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

    for photo in photos:
        contents = await photo.read()
        if not contents:
            continue

        _, ext = os.path.splitext(photo.filename)
        if not ext:
            continue

        filename = os.path.join(dir_name, f"{count}{ext}")
        with open(filename, "wb") as f:
            f.write(contents)

        count += 1

    return RedirectResponse(url="/dashboard", status_code=303)


@app.post("/delete-member")
async def delete_member(member: str = Form(...)):
    dir_name = os.path.join("..", "data", "members_data", member)

    members = get_members()
    if member in members:
        members.remove(member)
        write_members(members)
    
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)

    return RedirectResponse(url="/dashboard", status_code=303)