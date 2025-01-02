from urllib import request
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.s3 import S3Service
from src.app.tasks.tasks import send_confirmation_email
from src.app.models import User
from src.app.core.database import get_auth_service, get_db, get_s3_service
from src.app.schemas.shemas import SUserOutput, SUserRegister
from src.app.services.auth import AuthService, UserService

from pydantic import EmailStr, parse_obj_as
router = APIRouter(prefix="/auth", tags=["Auth & Пользователи"],)


@router.post("/register")
async def register_user(
    name: str = Form(..., description="User's full name"),
    email: EmailStr = Form(..., description="User's email address"),
    password: str = Form(..., description="User's password"),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
    s3_service: S3Service = Depends(get_s3_service)
):
    user_data = SUserRegister(name=name, email=email, password=password)
    user_service = UserService(db, auth_service)
    user = await user_service.register_user(user_data)
    user_dict = parse_obj_as(SUserRegister, user_data).dict()
    send_confirmation_email.delay(user_dict)
    s3_service.create_user_folder(user.id)

    return {"message": f"user: {user.name} successfully registered"}


@ router.post("/login")
async def login_user(
    response: Response,
    name: str = Form(..., description="User's full name"),
    email: EmailStr = Form(..., description="User's email address"),
    password: str = Form(..., description="User's password"),
    auth_service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db)
):
    user_data = SUserRegister(name=name, email=email, password=password)
    user_service = UserService(db, auth_service)
    await user_service.login_user(user_data, response)
    return {"message": "Login successful"}


@ router.post("/logout")
async def logout_user(
    response: Response,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=400, detail="No active session")

    await auth_service.delete_session(session_token)
    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}


@router.get("/me")
async def read_users_me(
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)
    return SUserOutput(name=current_user.name, email=current_user.email)
