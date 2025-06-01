from pydantic import BaseModel

class TokenResponse(BaseModel):
    token: str

class UserPasswordChange(BaseModel):
    password: str
    password_confirm: str

class PasswordChangeResponse(BaseModel):
    success: bool
