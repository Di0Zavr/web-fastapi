from fastapi import FastAPI, Depends
from db import init_db, get_session
from models import *
from typing import TypedDict, Union
from sqlmodel import select

HTTPResponse = TypedDict('HTTPResponse', {"status": int, "detail": str})
HTTP404 = {"status": 404, "detail": "not found"}
HTTP202 = {"status": 202, "detail": "accepted"}
HTTP201 = {"status": 201, "detail": "created"}
HTTP200 = {"status": 200, "detail": "ok"}

app = FastAPI()
@app.on_event('startup')
def on_startup():
    init_db()

@app.get("/test")
def test():
    return {"test": "test"}

@app.get("/users", response_model=List[UserResponse])
def get_user_list(session=Depends(get_session)) -> List[User]:
    return session.exec(select(User)).all()

@app.get("/user/{id}", response_model=Union[UserResponse, HTTPResponse])
def get_user_by_id(id: int, session=Depends(get_session)) -> Union[HTTPResponse, User]:
    db_record = session.get(User, id)
    if not db_record:
        return HTTP404
    return db_record

@app.post("/user/add")
def create_user(model: UserDefault, session=Depends(get_session)) -> HTTPResponse:
    model = User.model_validate(model)
    session.add(model)
    session.commit()
    session.refresh(model)
    return HTTP201

@app.patch("/user/update")
def update_user(id: int, model: UserDefault, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(User, id)
    if not db_record:
        return HTTP404
    data = User.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    session.add(db_record)
    session.commit()
    session.refresh(db_record)
    return HTTP200

@app.delete("/user/delete")
def delete_user(id: int, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(User, id)
    if not db_record:
        return HTTP404
    session.delete(db_record)
    session.commit()
    return HTTP200

@app.get("/hackathons", response_model=List[HackathonResponse])
def get_hackathon_list(session=Depends(get_session)) -> List[Hackathon]:
    return session.exec(select(Hackathon)).all()

@app.get("/hackathon/{id}", response_model=Union[HackathonResponse, HTTPResponse])
def get_hackathon_by_id(id: int, session=Depends(get_session)) -> Union[HTTPResponse, Hackathon]:
    db_record = session.get(Hackathon, id)
    if not db_record:
        return HTTP404
    return db_record

@app.post("/hackathon/add")
def create_hackathon(model: HackathonDefault, session=Depends(get_session)) -> HTTPResponse:
    model = Hackathon.model_validate(model)
    user = session.get(User, model.organizer_id)
    if not user:
        return HTTP404
    session.add(model)
    session.commit()
    session.refresh(model)
    return HTTP201

@app.patch("/hackathon/update")
def update_hackathon(id: int, model: HackathonDefault, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(Hackathon, id)
    if not db_record:
        return HTTP404
    data = Hackathon.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    session.add(db_record)
    session.commit()
    session.refresh(db_record)
    return HTTP200

@app.delete("/hackathon/delete")
def delete_hackathon(id: int, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(Hackathon, id)
    if not db_record:
        return HTTP404
    session.delete(db_record)
    session.commit()
    return HTTP200

@app.get("/hackathon/{hack_id}/teams", response_model=Union[HTTPResponse, List[TeamResponse]])
def get_hackathon_team_list(hack_id: int, session=Depends(get_session)) -> Union[HTTPResponse, List[Team]]:
    hackathon = session.get(Hackathon, hack_id)
    if not hackathon:
        return HTTP404
    return hackathon.teams

@app.get("/team/{id}", response_model=Union[TeamResponse, HTTPResponse])
def get_team_by_id(id: int, session=Depends(get_session)) -> Union[HTTPResponse, Team]:
    db_record = session.get(Team, id)
    if not db_record:
        return HTTP404
    return db_record

@app.post("/team/add")
def create_team(model: TeamDefault, session=Depends(get_session)) -> HTTPResponse:
    model = Team.model_validate(model)
    hackathon = session.get(Hackathon, model.hackathon_id)
    if not hackathon:
        return HTTP404
    session.add(model)
    session.commit()
    session.refresh(model)
    return HTTP201

@app.patch("/team/update")
def update_team(id: int, model: TeamDefault, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(Team, id)
    if not db_record:
        return HTTP404
    data = Team.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    try:
        session.add(db_record)
        session.commit()
        session.refresh(db_record)
    except:
        return HTTP404
    return HTTP200

@app.delete("/team/delete")
def delete_team(id: int, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(Team, id)
    if not db_record:
        return HTTP404
    session.delete(db_record)
    session.commit()
    return HTTP200

@app.post("/team/add_user")
def create_teammate(model: Teammate, session=Depends(get_session)) -> HTTPResponse:
    model = Teammate.model_validate(model)
    team = session.get(Team, model.team_id)
    user = session.get(User, model.user_id)
    if not team or not user:
        return HTTP404
    possible_teammate = session.get(Teammate, (model.team_id, model.user_id))
    if possible_teammate:
        return HTTP202
    session.add(model)
    session.commit()
    session.refresh(model)
    return HTTP201

@app.delete("/team/remove_user")
def delete_teammate(model: Teammate, id: int=None, session=Depends(get_session)) -> HTTPResponse:
    model = Teammate.model_validate(model)
    db_record = session.get(Teammate, (model.team_id, model.user_id))
    if not db_record:
        return HTTP404
    session.delete(db_record)
    session.commit()
    return HTTP200

@app.get("/user/{id}/teams", response_model=Union[List[TeamResponse], HTTPResponse])
def get_user_teams(id: int, session=Depends(get_session)) -> Union[List[Team], HTTPResponse]:
    user = session.get(User, id)
    if not user:
        return HTTP404
    teams = user.teams
    return teams

@app.get("/team/{id}/users", response_model=Union[List[UserResponse], HTTPResponse])
def get_team_users(id: int, session=Depends(get_session)) -> Union[List[User], HTTPResponse]:
    team = session.get(Team, id)
    if not team:
        return HTTP404
    users = team.users
    return users

@app.post("/task/create")
def create_task(model: TaskDefault, session=Depends(get_session)) -> HTTPResponse:
    model = Task.model_validate(model)
    print(model)
    hackathon = session.get(Hackathon, model.hackathon_id)
    if not hackathon:
        return HTTP404
    session.add(model)
    session.commit()
    session.refresh(model)
    return HTTP201

@app.get("/task/{id}", response_model=Union[TaskResponse, HTTPResponse])
def get_task_by_id(id: int, session=Depends(get_session)) -> Union[Task, HTTPResponse]:
    db_record = session.get(Task, id)
    if not db_record:
        return HTTP404
    return db_record

@app.patch("/task/update")
def update_task(id: int, model: TaskDefault, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(Task, id)
    if not db_record:
        return HTTP404
    data = Task.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    try:
        session.add(db_record)
        session.commit()
        session.refresh(db_record)
    except:
        return HTTP404
    return HTTP200

@app.delete("/task/delete")
def delete_task(id: int, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(Task, id)
    if not db_record:
        return HTTP404
    session.delete(db_record)
    session.commit()
    return HTTP200

@app.get("/solution/{id}", response_model=Union[TeamTaskSolutionResponse, HTTPResponse])
def get_solution_by_id(id: int, session=Depends(get_session)) -> Union[TeamTaskSolution, HTTPResponse]:
    db_record = session.get(TeamTaskSolution, id)
    if not db_record:
        return HTTP404
    return db_record

@app.get("/team/{id}/solutions", response_model=Union[List[TeamTaskSolutionResponse], HTTPResponse])
def get_team_solutions(id: int, session=Depends(get_session)) -> Union[List[TeamTaskSolution], HTTPResponse]:
    team = session.get(Team, id)
    if not team:
        return HTTP404
    print(team.solutions)
    return team.solutions

@app.get("/task/{id}/solutions", response_model=Union[List[TeamTaskSolutionResponse], HTTPResponse])
def get_task_solutions(id: int, session=Depends(get_session)) -> Union[List[TeamTaskSolution], HTTPResponse]:
    task = session.get(Task, id)
    if not task:
        return HTTP404
    return task.solutions

@app.get("/hackathon/{id}/solutions", response_model=List[TeamTaskSolutionResponse])
def get_hackathon_solutions(id: int, session=Depends(get_session)) -> List[TeamTaskSolution]:
    query = select(TeamTaskSolution) \
            .join(Task, TeamTaskSolution.task_id == Task.id) \
            .where(Task.hackathon_id == id)
    return session.exec(query)

@app.post("/solution/create")
def create_solution(model: TeamTaskSolutionDefault, session=Depends(get_session)) -> HTTPResponse:
    model = TeamTaskSolution.model_validate(model)
    team = session.get(Team, model.team_id)
    task = session.get(Task, model.task_id)
    if not team or not task:
        return HTTP404
    session.add(model)
    session.commit()
    session.refresh(model)
    return HTTP201

@app.patch("/solution/update")
def update_solution(id: int, model: TeamTaskSolutionDefault, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(TeamTaskSolution, id)
    if not db_record:
        return HTTP404
    data = Task.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    try:
        session.add(db_record)
        session.commit()
        session.refresh(db_record)
    except:
        return HTTP404
    return HTTP200

@app.delete("/solution/delete")
def delete_solution(id: int, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(TeamTaskSolution, id)
    if not db_record:
        return HTTP404
    session.delete(db_record)
    session.commit()
    return HTTP200

@app.get("/solution/{id}/fixes", response_model=Union[List[SolutionFixResponse], HTTPResponse])
def get_solution_fixes(id: int, session=Depends(get_session)) -> Union[List[SolutionFix], HTTPResponse]:
    solution = session.get(TeamTaskSolution, id)
    if not solution:
        return HTTP404
    return solution.fixes

@app.post("/solution/fix/create")
def create_solution_fix(model: SolutionFixDefault, session=Depends(get_session)) -> HTTPResponse:
    model = SolutionFix.model_validate(model)
    solution = session.get(TeamTaskSolution, model.solution_id)
    if not solution:
        return HTTP404
    session.add(model)
    session.commit()
    session.refresh(model)
    return HTTP201

@app.patch("/solution/fix/update")
def update_solution_fix(id: int, model: SolutionFixDefault, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(SolutionFix, id)
    if not db_record:
        return HTTP404
    data = SolutionFix.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    try:
        session.add(db_record)
        session.commit()
        session.refresh(db_record)
    except:
        return HTTP404
    return HTTP200

@app.delete("/solution/fix/delete")
def delete_solution_fix(id: int, session=Depends(get_session)) -> HTTPResponse:
    db_record = session.get(SolutionFix, id)
    if not db_record:
        return HTTP404
    session.delete(db_record)
    session.commit()
    return HTTP201


