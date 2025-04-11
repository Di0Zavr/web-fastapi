from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from db.db import get_session
from db.models import *
from starlette import status

team_router = APIRouter(prefix="/team", tags=["teams"])

@team_router.get("/{id}", response_model=TeamResponse)
def get_team_by_id(id: int, session=Depends(get_session)) -> Team:
    db_record = session.get(Team, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team was not found"
        )
    return db_record

@team_router.post("/create")
def create_team(model: TeamDefault, session=Depends(get_session)) -> JSONResponse:
    model = Team.model_validate(model)
    hackathon = session.get(Hackathon, model.hackathon_id)
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon was not found"
        )
    session.add(model)
    session.commit()
    session.refresh(model)
    return JSONResponse(
        content={"message": "Team was successfully created"},
        status_code=status.HTTP_201_CREATED
    )

@team_router.patch("/update")
def update_team(id: int, model: TeamDefault, session=Depends(get_session)) -> JSONResponse:
    db_record = session.get(Team, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team was not found"
        )
    data = Team.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    # pls remove this try i pray thee
    try:
        session.add(db_record)
        session.commit()
        session.refresh(db_record)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon was not found"
        )
    return JSONResponse(
        content={"message": "Team was successfully updated"},
        status_code=status.HTTP_200_OK
    )

@team_router.delete("/{id}")
def delete_team(id: int, session=Depends(get_session)) -> JSONResponse:
    db_record = session.get(Team, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team was not found"
        )
    session.delete(db_record)
    session.commit()
    return JSONResponse(
        content={"message": "Team was successfully deleted"},
        status_code=status.HTTP_200_OK
    )

@team_router.post("/add_user")
def create_teammate(model: Teammate, session=Depends(get_session)) -> JSONResponse:
    model = Teammate.model_validate(model)
    team = session.get(Team, model.team_id)
    user = session.get(User, model.user_id)
    if not team or not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team and/or user was not found"
        )
    possible_teammate = session.get(Teammate, (model.team_id, model.user_id))
    if possible_teammate:
        return JSONResponse(
            content={"User already in this team"},
            status_code=status.HTTP_202_ACCEPTED
        )
    session.add(model)
    session.commit()
    session.refresh(model)
    return JSONResponse(
        content={"User was added in team successfully"},
        status_code=status.HTTP_201_CREATED
    )

@team_router.delete("/remove_user")
def delete_teammate(model: Teammate, id: int=None, session=Depends(get_session)) -> JSONResponse:
    model = Teammate.model_validate(model)
    db_record = session.get(Teammate, (model.team_id, model.user_id))
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not in team"
        )
    session.delete(db_record)
    session.commit()
    return JSONResponse(
        content={"message": "User was removed from team successfully"}
    )

@team_router.get("/{id}/users", response_model=List[UserResponse])
def get_team_users(id: int, session=Depends(get_session)) -> List[User]:
    team = session.get(Team, id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team was not found"
        )
    users = team.users
    return users

@team_router.get("/{id}/solutions", response_model=List[TeamTaskSolutionResponse])
def get_team_solutions(id: int, session=Depends(get_session)) -> List[TeamTaskSolution]:
    team = session.get(Team, id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team was not found"
        )
    return team.solutions
