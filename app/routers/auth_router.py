from fastapi import APIRouter, Depends, HTTPException
from db.models import User, UserDefault, UserResponse, UserLogin
from db.db import get_session
from sqlmodel import select, or_
from auth.auth_handler import get_password_hash, verify_password, encode_token
from dto.GeneralDto import TokenResponse

auth_router = APIRouter(prefix="/auth", tags=["/auth"])

@auth_router.post(
    "/register",
    response_model=UserResponse
)
def register(model: UserDefault, session=Depends(get_session)) -> UserResponse:
    model = User.model_validate(model)
    if session.exec(select(User)
                    .where(
                        or_(User.username == model.username,
                            User.email == model.email)
                        )).first():
        raise HTTPException(
            status_code=400,
            detail="User with this username or email already exists"
        )
    hashed_password = get_password_hash(model.password)
    model.password = hashed_password

    session.add(model)
    session.commit()
    session.refresh(model)

    result = session.exec(select(User).where(User.username == model.username)).first()
    return result

@auth_router.post(
    "/login",
    response_model=TokenResponse
)
def login(model: UserLogin, session=Depends(get_session)) -> TokenResponse:
    model = UserLogin.model_validate(model)
    user = session.exec(
        select(User)
        .where(User.username == model.username)
    ).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid username and/or password"
        )
    if not verify_password(model.password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Invalid username and/or password"
        )
    jwt_token = encode_token(user.id, user.role)
    return TokenResponse(token=jwt_token)