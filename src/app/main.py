import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from src.app.services.auth import AuthService
from src.app.resources.user_router import router as user_routers
from src.app.resources.file_router import router as files_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = await redis.from_url("redis://redis:6379")
    app.state.redis = redis_client
    app.state.auth_service = AuthService(redis_client)
    yield
    await redis_client.close()


def get_app() -> FastAPI:
    app = FastAPI(
        title="My Google Disk",
        description="Author - Denis Sergeev",
        debug=True
    )
    app.include_router(router=user_routers)
    app.include_router(router=files_routers)
    app.router.lifespan_context = lifespan
    return app
