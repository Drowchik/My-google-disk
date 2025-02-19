
import json
import uuid
from fastapi import HTTPException, Request, Response

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import Folder, User
from sqlalchemy import select
from src.app.schemas.shemas import SUserRegister
from passlib.context import CryptContext


class AuthService:
    def __init__(self, redis):
        self.redis = redis
        self.session_prefix = "session:"
        self.session_expire = 3600
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_session_token(self) -> str:
        return str(uuid.uuid4())

    def set_session_cookie(self, response: Response, session_token: str) -> None:
        response.set_cookie(
            "session_token", session_token,
            httponly=True, max_age=self.session_expire,
            secure=True, samesite="Lax"
        )

    async def save_session(self, session_token: str, session_data: dict) -> None:
        await self.redis.setex(
            f"{self.session_prefix}{session_token}",
            self.session_expire,
            json.dumps(session_data)
        )

    async def get_session(self, session_token: str) -> dict | None:
        session_key = f"{self.session_prefix}{session_token}"
        session_data = await self.redis.get(session_key)
        if not session_data:
            return None
        return json.loads(session_data)

    async def delete_session(self, session_token: str) -> None:
        session_key = f"{self.session_prefix}{session_token}"
        await self.redis.delete(session_key)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hash_password: str) -> bool:
        return self.pwd_context.verify(password, hash_password)


class UserService:
    def __init__(self, db: AsyncSession, auth_service: AuthService = None):
        self.db = db
        self.auth_service = auth_service

    async def get_user_by_filter(self, **kwargs) -> User | None:
        result = await self.db.execute(select(User).filter_by(**kwargs))
        return result.scalar()

    async def get_by_path(self, path: str):
        print(path, "PATH")
        result = await self.db.execute(select(Folder).filter(Folder.name == path))
        return result.scalar()

    async def create_user(self, email, name: str, hashed_password: str) -> User:
        new_user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def register_user(self, user_data: SUserRegister) -> User:
        existing_user = await self.get_user_by_filter(email=user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Email already registered")

        return await self.create_user(
            email=user_data.email,
            hashed_password=self.auth_service.get_password_hash(
                user_data.password
            ),
            name=user_data.name
        )

    async def login_user(self, user_data: SUserRegister, response: Response) -> str:
        existing_user = await self.get_user_by_filter(email=user_data.email)
        if not existing_user or not self.auth_service.verify_password(user_data.password, existing_user.hashed_password):
            raise HTTPException(status_code=400, detail="Email not registered")

        session_token = self.auth_service.create_session_token()
        session_data = {"user_id": existing_user.id,
                        "email": existing_user.email}
        await self.auth_service.save_session(session_token, session_data)
        self.auth_service.set_session_cookie(response, session_token)

    async def get_current_user(self, request: Request) -> User:
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        session_data = await self.auth_service.get_session(session_token)
        if not session_data:
            raise HTTPException(
                status_code=401, detail="Session expired or invalid")

        user = await self.get_user_by_filter(id=session_data["user_id"])
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
