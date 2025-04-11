from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from db.db import get_session
from db.models import *
from sqlmodel import select
from starlette import status

hackathon_router = APIRouter(prefix="/hackathon", tags=["hackathons"])

@hackathon_router.get("/list", response_model=List[HackathonResponse])
def get_hackathon_list(session=Depends(get_session)) -> List[Hackathon]:
    return session.exec(select(Hackathon)).all()

@hackathon_router.get("/{id}", response_model=HackathonResponse)
def get_hackathon_by_id(id: int, session=Depends(get_session)) -> Hackathon:
    db_record = session.get(Hackathon, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon was not found"
        )
    return db_record

@hackathon_router.post("/create")
def create_hackathon(model: HackathonDefault, session=Depends(get_session)) -> JSONResponse:
    model = Hackathon.model_validate(model)
    user = session.get(User, model.organizer_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon was not found"
        )
    session.add(model)
    session.commit()
    session.refresh(model)
    return JSONResponse(
        content={"message": "Hackathon was successfully created"},
        status_code=status.HTTP_201_CREATED
    )

@hackathon_router.patch("/update")
def update_hackathon(id: int, model: HackathonDefault, session=Depends(get_session)) -> JSONResponse:
    db_record = session.get(Hackathon, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon was not found"
        )
    data = Hackathon.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    session.add(db_record)
    session.commit()
    session.refresh(db_record)
    return JSONResponse(
        content={"message": "Hackathon was successfully created"}
    )

@hackathon_router.delete("/{id}")
def delete_hackathon(id: int, session=Depends(get_session)) -> JSONResponse:
    db_record = session.get(Hackathon, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon was not found"
        )
    session.delete(db_record)
    session.commit()
    return JSONResponse(
        content={"message": "Hackathon was successfully deleted"}
    )

@hackathon_router.get("/{hack_id}/teams", response_model=List[TeamResponse])
def get_hackathon_team_list(hack_id: int, session=Depends(get_session)) -> List[Team]:
    hackathon = session.get(Hackathon, hack_id)
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon was not found"
        )
    return hackathon.teams

@hackathon_router.get("/{id}/solutions", response_model=List[TeamTaskSolutionResponse])
def get_hackathon_solutions(id: int, session=Depends(get_session)) -> List[TeamTaskSolution]:
    hackathon = session.get(Hackathon, id)
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon was not found"
        )
    query = select(TeamTaskSolution) \
            .join(Task, TeamTaskSolution.task_id == Task.id) \
            .where(Task.hackathon_id == id)
    return session.exec(query)
