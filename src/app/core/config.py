from dynaconf import Dynaconf
from pydantic import AnyUrl
from pydantic_settings import BaseSettings

_settings = Dynaconf(
    settings_files=["config.yaml"]
)
_project_timezone = "Europe/Moscow"

_db_dsn = AnyUrl.build(
    scheme="postgresql+asyncpg",
    username=_settings.database.user,
    password=_settings.database.password,
    host=_settings.database.host,
    port=_settings.database.port,
    path=_settings.database.db,
)


class Settings(BaseSettings):
    db_dsn: str
    app_name: str
    timezone: str
    celery_broker: str
    email: str
    password: str
    smtp_host: str
    smtp_port: int
    aws_access_key_id: str
    aws_secret_access_key: str
    endpoint_url: str
    bucket_name: str


settings = Settings(
    db_dsn=str(_db_dsn),
    app_name="My Google Disk",
    timezone=_project_timezone,
    celery_broker=_settings.celery.broker,
    email=_settings.celery.email,
    password=_settings.celery.password,
    smtp_host=_settings.celery.smtp_host,
    smtp_port=_settings.celery.smtp_port,
    aws_access_key_id=_settings.selectel.aws_access_key_id,
    aws_secret_access_key=_settings.selectel.aws_secret_access_key,
    endpoint_url=_settings.selectel.endpoint_url,
    bucket_name=_settings.selectel.bucket_name,
)
