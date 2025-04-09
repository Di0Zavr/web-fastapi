from datetime import datetime
from typing import Optional, List
from typing_extensions import TypedDict
from enum import Enum
from fastapi import FastAPI

from pydantic import BaseModel

class UserRole(Enum):
    user = "user"
    admin = "admin"
    organizer = "organizer"

class User(BaseModel):
    id: int
    username: str
    password: str
    email: str
    phone: str
    role: UserRole

class Task(BaseModel):
    id: int
    name: str
    description: str
    technical_task: str
    requirements: Optional[str] = ''
    grading_criteria: Optional[str] = ''

class Hackathon(BaseModel):
    id: int
    name: str
    description: str
    participant_conditions: Optional[str] = ''
    location: str
    organizer: User
    start_date: datetime
    end_date: datetime
    tasks: Optional[List[Task]] = []

HttpResponce = TypedDict('HttpResponce', {"status": int, "message": str})


db = [
    {
        "id": 1,
        "name":"Data Fusion",
        "description":"hackathon for ai developers and data scientists",
        "participation_conditions":"be a good boy",
        "location":"Moscow",
        "organizer": {
            "id": 1,
            "username": "Cool Moscow Univeristy",
            "password": "482c811da5d5b4bc6d497ffa98491e38",
            "email":"MoscowUniversity@gmail.com",
            "phone":"89999999999",
            "role":"organizer"
        },
        "start_date":datetime(2025, 3, 25, 12, 0, 0),
        "end_date":datetime(2025, 3, 27, 12, 0, 0),
        "tasks":[
            {
                "id": 1,
                "name": "AI task",
                "description":"very important task",
                "technical_task":"do some ai things",
                "requirements":"can use python",
                "grading_criteria": "1 is bad and 5 is good"
            },
            {
                "id":2,
                "name": "Data task",
                "description":"very important data task",
                "technical_task":"do some interesting things with provided data",
                "requirements":"can use python and brain",
                "grading_criteria":"1 is bad and 5 is good"
            }
        ]
    },
    {
        "id":2,
        "name":"Sibirean Gamejam",
        "description":"do your cool game here",
        "participation_conditions":"be enthusiastic",
        "location":"Novosibirsk",
        "organizer":{
            "id":2,
            "username":"Novosibirsk State University",
            "password":"596a96cc7bf9108cd896f33c44aedc8a",
            "email":"GameJamSibirb@gmail.com",
            "phone": "89999999998",
            "role":"organizer"
        },
        "start_date":datetime(2025, 4, 25, 12, 0, 0),
        "end_date":datetime(2025, 4, 27, 12, 0, 0),
        "tasks":[
            {
                "id":3,
                "name":"Platformer game",
                "description":"do basic things with interesting idea",
                "technical_task":"do game where you can jump on platforms",
                "requirements":"can click on a keyboard, optionally - know Unity",
                "grading_criteria":"100 points is maximum"
            }
        ]
    }
]

app = FastAPI()

@app.get("/")
def lol():
    return 'lol'

@app.get("/hackathon")
def get_hackathon_list() -> List[Hackathon]:
    return db

@app.get("/hackathon/{hack_id}")
def get_hackathon_by_id(hack_id: int) -> List[Hackathon]:
    return [hack for hack in db if hack.get("id") == hack_id]

@app.post("/hackathon/add")
def create_hackathon(hackathon: Hackathon) -> HttpResponce:
    db.append(hackathon)
    return {"status": 201, "message": "created"}

@app.delete("/hackathon/{hack_id}")
def delete_hackathon(hack_id: int) -> HttpResponce:
    for i, hackathon in enumerate(db):
        if hackathon.get("id") == hack_id:
            db.pop(i)
            break
    return {"status": 200, "message": "OK"}

@app.put("/hackathon/{hack_id}")
def update_hackathon(hack_id: int, hackathon: Hackathon) -> HttpResponce:
    for i, hack in enumerate(db):
        if hack.get("id") == hack_id:
            db[i] = hackathon
    return {"status": 200, "message": "OK"}

@app.get("/hackathon/{hack_id}/task")
def get_task_list(hack_id: int) -> List[Task]:
    for hack in db:
        if hack.get("id") == hack_id:
            tasks = hack.get("tasks")
            break
    return tasks

@app.get("/task/{task_id}")
def get_task_by_id(task_id: int) -> List[Task]:
    tasks = []
    for hack in db:
        collection = hack.get("tasks")
        if not collection:
            continue
        tasks.extend(collection)
    # print(tasks)
    return [task for task in tasks if task.get("id") == task_id]

@app.post("/task/add")
def create_task(hack_id: int, task: Task) -> HttpResponce:
    for hack in db:
        if hack.get("id") != hack_id:
            continue
        if not hack.get("tasks"):
            continue
        hack["tasks"].append(task)
        break
    
    return {"status": 201, "message": "created"}

@app.delete("/task/{task_id}")
def delete_task(task_id: int) -> HttpResponce:
    for i, hack in enumerate(db):
        if not hack.get("tasks"):
            continue
        for j, task in enumerate(hack["tasks"]):
            if isinstance(task, dict) and task.get("id") == task_id \
                or isinstance(task, Task) and task.id == task_id:
                # из-за того что у нас временная дб в питоновском джосе (т.е. словаре)
                # и мы работаем с моделями получается так, что у нас в дб намешаны и словари и модели
                # которые имеют разные методы и надо как-то с этим работать
                db[i]["tasks"].pop(j)
                break
    return {"status": 200, "message": "OK"}

@app.put("/task/update")
def update_task(task: Task) -> HttpResponce:
    task_id = task.id
    for i, hack in enumerate(db):
        if not hack.get("tasks"):
            continue
        for j, task_ in enumerate(hack["tasks"]):
            if isinstance(task_, dict) and task_.get("id") == task_id \
                or isinstance(task_, Task) and task_.id == task_id:
                # из-за того что у нас временная дб в питоновском джосе (т.е. словаре)
                # и мы работаем с моделями получается так, что у нас в дб намешаны и словари и модели
                # которые имеют разные методы и надо как-то с этим работать
                db[i]["tasks"][j] = task
                break
    return {"status": 200, "message": "OK"}

