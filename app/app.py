from fastapi import FastAPI
from db.db import init_db
from db.models import *
from routers.user_router import user_router
from routers.hackathon_router import hackathon_router
from routers.team_router import team_router
from routers.task_router import task_router
from routers.solution_router import solution_router, fix_router
from routers.auth_router import auth_router
import requests

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(hackathon_router)
app.include_router(team_router)
app.include_router(task_router)
solution_router.include_router(fix_router)
app.include_router(solution_router)

@app.on_event('startup')
def on_startup():
    init_db()

@app.get("/")
def test():
    return {"test": "test"}

@app.post("/parse")
def parse(size: int=10, slice: int=1):
    session = requests.Session()
    try:
        r = session.post("http://parser-app:9000/parse",
                    params={"size": size, "slice": slice})
    except requests.exceptions.ConnectionError:
        return {"detail": "connection error"}
    if r.ok:
        return r.json()
    else:
        return {"ok": False}

@app.post("/parse_url")
def parse_url(url: str):
    session = requests.Session()
    try:
        r = session.post("http://parser-app:9000/parse_url",
                         params={"url": url})
    except requests.exceptions.ConnectionError:
        return {"detail": "connection error"}
    
    if r.ok:
        return r.json()
    else:
        return {"ok": False}