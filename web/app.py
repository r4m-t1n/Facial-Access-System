import os
import json
from fastapi import FastAPI, Form, Body, Request
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

def add_member(member: str):
    data = get_members()
    data.append(member)

    with open('../data/members.json', 'w') as file:
        json.dump(data, file, indent=4)

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

    add_member(new_member)
    
    os.makedirs(
        os.path.join("..", "data", "members_data", new_member), exist_ok=True
    )

    return JSONResponse(content={"status": "success"}, status_code=200)