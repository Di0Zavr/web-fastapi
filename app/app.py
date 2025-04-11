from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse #
from db.db import init_db, get_session
from db.models import *
from typing import TypedDict, Union #
from sqlmodel import select, or_ #
from starlette import status #
from auth.auth_handler import AuthHandler #
from routers.user_router import user_router
from routers.hackathon_router import hackathon_router
from routers.team_router import team_router
from routers.task_router import task_router
from routers.solution_router import solution_router, fix_router

HTTPResponse = TypedDict('HTTPResponse', {"status": int, "detail": str})
HTTP404 = {"status": 404, "detail": "not found"}
HTTP202 = {"status": 202, "detail": "accepted"}
HTTP201 = {"status": 201, "detail": "created"}
HTTP200 = {"status": 200, "detail": "ok"}

auth_handler = AuthHandler()

app = FastAPI()
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

@app.post("/register")
def register(model: UserDefault, session=Depends(get_session)) -> HTTPResponse:
    model = User.model_validate(model)
    if session.exec(select(User)
                    .where(
                        or_(User.username == model.username,
                            User.email == model.email)
                        )).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists"
        )
    hashed_password = auth_handler.get_password_hash(model.password)
    model.password = hashed_password

    session.add(model)
    session.commit()
    session.refresh(model)
    return HTTP200

@app.post("/login")
def login(model: UserLogin, session=Depends(get_session)):
    model = UserLogin.model_validate(model)
    user = session.exec(
        select(User)
        .where(User.username == model.username)
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username and/or password"
        )
    if not auth_handler.verify_password(model.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username and/or password"
        )
    jwt_token = auth_handler.encode_token(user.id, user.role)
    response = RedirectResponse(url="/",
                                status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session", value=jwt_token, secure=True)

