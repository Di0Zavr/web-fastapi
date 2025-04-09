from typing import Union, TypedDict
from fastapi import FastAPI, Depends
from models import *
from db import init_db, get_session
from sqlmodel import select

HTTPResponse = TypedDict('HTTPResponse', {"status": int, "detail": str})

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"message": "sky_rocketed"}

@app.get("/users", response_model=List[UserResponse])
def get_user_list(session=Depends(get_session)) -> List[User]:
    return session.exec(select(User)).all()

@app.get("/user/{id}", response_model=UserResponse)
def get_user_by_id(id: int, session=Depends(get_session)) -> Union[HTTPResponse, User]:
    db_record = session.get(User, id)
    if not db_record:
        return {"status": 404, "detail": "not found"}
    return db_record

@app.post("/user/add")
def create_user(model: UserDefault, session=Depends(get_session)) -> HTTPResponse:
    model = User.model_validate(model)
    session.add(model)
    session.commit()
    session.refresh(model)
    return {"status": 201, "detail": "created"}

@app.patch("/user/update")
def update_user(id: int, model: UserDefault, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(User, id)
    if not db_record:
        return {"status": 404, "detail": "not found"}
    data = User.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    session.add(db_record)
    session.commit()
    session.refresh(db_record)
    return {"status": 200, "detail": "ok"}

@app.delete("/user/delete")
def delete_user(id: int, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(User, id)
    if not db_record:
        return {"status": 404, "detail": "not found"}
    session.delete(db_record)
    session.commit()
    return {"status": 200, "detail": "ok"}

@app.get("/hackathons", response_model=List[HackathonResponse])
def get_hackathon_list(session=Depends(get_session)) -> List[Hackathon]:
    return session.exec(select(Hackathon)).all()

@app.get("/hackathon/{id}", response_model=HackathonResponse)
def get_hackathon_by_id(id: int, session=Depends(get_session)) -> Union[HTTPResponse, Hackathon]:
    db_record = session.get(Hackathon, id)
    if not db_record:
        return {"status": 404, "detail": "not found"}
    return db_record

@app.post("/hackathon/add")
def create_hackathon(model: HackathonDefault, session=Depends(get_session)) -> HTTPResponse:
    model = Hackathon.model_validate(model)
    session.add(model)
    session.commit()
    session.refresh(model)
    return {"status": 201, "detail": "created"}

@app.patch("/hackathon/update")
def update_hackathon(id: int, model: HackathonDefault, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(Hackathon, id)
    if not db_record:
        return {"status": 404, "detail": "not found"}
    data = Hackathon.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    session.add(db_record)
    session.commit()
    session.refresh(db_record)
    return {"status": 200, "detail": "ok"}

@app.delete("/hackathon/delete")
def delete_hackathon(id: int, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(Hackathon, id)
    if not db_record:
        return {"status": 404, "detail": "not found"}
    session.delete(db_record)
    session.commit()
    return {"status": 200, "detail": "ok"}

@app.get("/hackathon/{hack_id}/teams", response_model=List[TeamResponse])
def get_hackathon_team_list(hack_id: int, session=Depends(get_session)) -> Union[HTTPResponse, List[Team]]:
    hackathon = session.get(Hackathon, hack_id)
    if not hackathon:
        return {"status": 404, "detail": "not found"}
    return session.exec(select(Team).where(Team.hackathon_id == hack_id)).all()

@app.get("/team/{id}", response_model=TeamResponse)
def get_team_by_id(id: int, session=Depends(get_session)) -> Union[HTTPResponse, Team]:
    db_record = session.get(Team, id)
    if not db_record:
        return {"status": 404, "detail": "not found"}
    return db_record

@app.post("/team/add")
def create_team(model: TeamDefault, session=Depends(get_session)) -> HTTPResponse:
    model = Team.model_validate(model)
    hackathon = session.get(Hackathon, model.hackathon_id)
    if not hackathon:
        return {"status": 404, "detail": "not found"}
    session.add(model)
    session.commit()
    session.refresh(model)
    return {"status": 201, "detail": "created"}

@app.patch("/team/update")
def update_team(id: int, model: TeamDefault, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(Team, id)
    if not db_record:
        return {"status": 404, "detail": "not found"}
    data = Team.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    try:
        session.add(db_record)
        session.commit()
        session.refresh(db_record)
    except:
        return {"status": 404, "detail": "not found"}
    return {"status": 200, "detail": "ok"}

@app.delete("/team/delete")
def delete_team(id: int, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(Team, id)
    if not db_record:
        return {"status": 404, "detail": "not found"}
    session.delete(db_record)
    session.commit()
    return {"status": 200, "detail": "ok"}

@app.post("/team/add_user")
def create_teammate(model: Teammate, session=Depends(get_session)) -> HTTPResponse:
    model = Teammate.model_validate(model)  # maybe check if fields is None
    team = session.get(Team, model.team_id)
    user = session.get(User, model.user_id)
    if not team or not user:
        return {"status": 404, "detail": "not found"}
    possible_teammate = session.get(Teammate, (model.team_id, model.user_id))
    if possible_teammate:
        return {"status": 202, "detail": "accepted"}
    session.add(model)
    session.commit()
    session.refresh(model)
    return {"status": 201, "detail": "created"}

@app.delete("/team/remove_user")
def delete_teammate(model: Teammate, id: int=None, session=Depends(get_session)) -> HTTPResponse:
    model = Teammate.model_validate(model)
    db_record = session.get(Teammate, (model.team_id, model.user_id))
    if not db_record:
        return {"status": 404, "detail": "not found"}
    session.delete(db_record)
    session.commit()
    return {"status": 200, "detail": "ok"}

@app.get("/user/{id}/teams", response_model=List[TeamResponse])
def get_user_teams(id: int, session=Depends(get_session)) -> Union[List[Team], HTTPResponse]:
    user = session.get(User, id)
    if not user:
        return {"status": 404, "detail": "not found"}
    teams = user.teams
    return teams

@app.get("/team/{id}/users", response_model=List[UserResponse])
def get_team_users(id: int, session=Depends(get_session)) -> Union[List[User], HTTPResponse]:
    team = session.get(Team, id)
    if not team:
        return {"status": 404, "detail": "not found"}
    users = team.users
    return users
