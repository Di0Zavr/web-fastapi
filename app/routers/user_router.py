from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from auth.auth_handler import get_current_user_id, get_password_hash
from db.db import get_session
from db.models import *
from dto.GeneralDto import PasswordChangeResponse, UserPasswordChange
from sqlmodel import select
from starlette import status

user_router = APIRouter(prefix="/user", tags=["user"])

@user_router.get("/me", response_model=UserResponse)
def get_me(
    session=Depends(get_session),
    user_id=Depends(get_current_user_id)
):
    return session.get(User, user_id)

@user_router.post(
        "/change-password",
        response_model=PasswordChangeResponse
        )
def change_password(
    data: UserPasswordChange,
    session=Depends(get_session),
    user_id=Depends(get_current_user_id)
):
    if data.password != data.password_confirm:
        raise HTTPException(
            status_code=400,
            detail="Пароли не совпадают"
        )
    db_record = session.get(User, user_id)
    password_hash = get_password_hash(data.password)
    db_record.password = password_hash
    try:
        session.add(db_record)
        session.commit()
        session.refresh(db_record)
    except Exception:
        return {"success": False}
    return {"success": True}

@user_router.get("/list", response_model=List[UserResponse])
def get_user_list(
    session=Depends(get_session)
) -> List[User]:
    return session.exec(select(User)).all()

@user_router.get("/{id}", response_model=UserResponse)
def get_user_by_id(id: int, session=Depends(get_session)) -> User:
    db_record = session.get(User, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found!"
        )
    return db_record

@user_router.patch("/update")
def update_user(id: int, model: UserDefault, session=Depends(get_session)) -> JSONResponse:
    db_record = session.get(User, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found!"
        )
    data = User.model_dump(model, exclude_unset=True)
    for key, value in data.items():
        setattr(db_record, key, value)
    session.add(db_record)
    session.commit()
    session.refresh(db_record)
    return JSONResponse(
        content={"message": "User was successfully updated"}
    )

@user_router.delete("/{id}")
def delete_user(id: int, session=Depends(get_session)) -> JSONResponse:
    db_record = session.get(User, id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found!"
        )
    session.delete(db_record)
    session.commit()
    return JSONResponse(
        content={"message": "User was successfully deleted"}
    )

@user_router.get("/{id}/teams", response_model=List[TeamResponse])
def get_user_teams(id: int, session=Depends(get_session)) -> List[Team]:
    user = session.get(User, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found"
        )
    teams = user.teams
    return teams
