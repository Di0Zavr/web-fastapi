from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from db.db import get_session
from db.models import *
from starlette import status

task_router = APIRouter(prefix="/task", tags=["tasks"])

@task_router.post("/create")
def create_task(model: TaskDefault, session=Depends(get_session)) -> JSONResponse:
    model = Task.model_validate(model)
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
        content={"message": "Task was successfully created"},
        status_code=status.HTTP_201_CREATED
    )

@task_router.get("/{id}", response_model=TaskResponse)
def get_task_by_id(id: int, session=Depends(get_session)) -> Task:
    db_record = session.get(Task, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task was not found"
        )
    return db_record

@task_router.patch("/update")
def update_task(id: int, model: TaskDefault, session=Depends(get_session)) -> JSONResponse:
    db_record = session.get(Task, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task was not found"
        )
    data = Task.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    # fix this try-except lol
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
        content={"message": "Task was successfully updated"}
    )

@task_router.delete("/{id}")
def delete_task(id: int, session=Depends(get_session)) -> JSONResponse:
    db_record = session.get(Task, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task was not found"
        )
    session.delete(db_record)
    session.commit()
    return JSONResponse(
        content={"message": "Task was successfully deleted"}
    )

@task_router.get("/{id}/solutions", response_model=List[TeamTaskSolutionResponse])
def get_task_solutions(id: int, session=Depends(get_session)) -> List[TeamTaskSolution]:
    task = session.get(Task, id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task was not found"
        )
    return task.solutions
