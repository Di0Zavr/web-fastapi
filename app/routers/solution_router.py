from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from db.db import get_session
from db.models import *
from starlette import status

fix_router = APIRouter(prefix="/fix", tags=["fixes"])
solution_router = APIRouter(prefix="/solution", tags=["solutions"])

@solution_router.get("/{id}", response_model=TeamTaskSolutionResponse)
def get_solution_by_id(id: int, session=Depends(get_session)) -> TeamTaskSolution:
    db_record = session.get(TeamTaskSolution, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution was not found"
        )
    return db_record

@solution_router.post("/create")
def create_solution(model: TeamTaskSolutionDefault, session=Depends(get_session)) -> JSONResponse:
    model = TeamTaskSolution.model_validate(model)
    team = session.get(Team, model.team_id)
    task = session.get(Task, model.task_id)
    if not team or not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team and/or task was not found"
        )
    session.add(model)
    session.commit()
    session.refresh(model)
    return JSONResponse(
        content={"message": "Solution was successfully crated"},
        status_code=status.HTTP_201_CREATED
    )

@solution_router.patch("/update")
def update_solution(id: int, model: TeamTaskSolutionDefault, session=Depends(get_session)) -> JSONResponse:
    db_record = session.get(TeamTaskSolution, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution was not found"
        )
    data = Task.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    # pls stop dude
    try:
        session.add(db_record)
        session.commit()
        session.refresh(db_record)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team and/or task was not found"
        )
    return JSONResponse(
        content={"message": "Solution was successfully updated"}
    )

@solution_router.delete("/{id}")
def delete_solution(id: int, session=Depends(get_session)) -> JSONResponse:
    db_record = session.get(TeamTaskSolution, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution was not found"
        )
    session.delete(db_record)
    session.commit()
    return JSONResponse(
        content={"message": "Solution was successfully deleted"}
    )

@solution_router.get("/{id}/fixes", response_model=List[SolutionFixResponse])
def get_solution_fixes(id: int, session=Depends(get_session)) -> List[SolutionFix]:
    solution = session.get(TeamTaskSolution, id)
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution was not found"
        )
    return solution.fixes

@fix_router.post("/create")
def create_solution_fix(model: SolutionFixDefault, session=Depends(get_session)) -> JSONResponse:
    model = SolutionFix.model_validate(model)
    solution = session.get(TeamTaskSolution, model.solution_id)
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution was not found"
        )
    session.add(model)
    session.commit()
    session.refresh(model)
    return JSONResponse(
        content={"message": "Fix was successfully created"},
        status_code=status.HTTP_201_CREATED
    )

@fix_router.patch("/update")
def update_solution_fix(id: int, model: SolutionFixDefault, session=Depends(get_session)) -> JSONResponse:
    db_record = session.get(SolutionFix, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution fix was not found"
        )
    data = SolutionFix.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    try:
        session.add(db_record)
        session.commit()
        session.refresh(db_record)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution was not found"
        )
    return JSONResponse(
        content={"message": "Solution fix was successfully updated"}
    )

@fix_router.delete("/{id}")
def delete_solution_fix(id: int, session=Depends(get_session)) -> JSONResponse:
    db_record = session.get(SolutionFix, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution fix was not found"
        )
    session.delete(db_record)
    session.commit()
    return JSONResponse(
        content={"message": "Solution fix was successfully"},
        status_code=status.HTTP_201_CREATED
    )
