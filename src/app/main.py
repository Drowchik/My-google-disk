import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from src.app.services.auth import AuthService
from src.app.resources.user_router import router as user_routers
from src.app.resources.file_router import router as files_routers
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = await redis.from_url("redis://localhost:6379")
    app.state.redis = redis_client
    app.state.auth_service = AuthService(redis_client)
    yield
    await redis_client.close()


def get_app() -> FastAPI:
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    app = FastAPI(
        title="My Google Disk",
        description="Author - Denis Sergeev",
        debug=True
    )
    app.include_router(router=user_routers)
    app.include_router(router=files_routers)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.router.lifespan_context = lifespan
    return app
