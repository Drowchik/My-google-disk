from io import BytesIO
from fastapi import APIRouter, Depends, File, Request, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession


from src.app.services.auth import AuthService, UserService
from src.app.core.database import get_auth_service, get_db, get_s3_service
from src.app.services.s3 import S3Service

router = APIRouter(prefix="/mydisk", tags=["Загрузка файлов"],)


@router.post("/files/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    s3_service: S3Service = Depends(get_s3_service),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)
    try:
        file_data = await file.read()
        s3_service.upload_file(current_user.id, file.filename, file_data)
        return {"message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
async def list_user_files(
    request: Request,
    s3_service: S3Service = Depends(get_s3_service),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Получить список файлов для текущего пользователя"""
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)

    try:
        files = s3_service.list_files(current_user.id)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files")
async def delete_file(
    request: Request,
    file_name: str,
    s3_service: S3Service = Depends(get_s3_service),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Удалить файл для текущего пользователя"""
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)

    try:
        s3_service.delete_file(current_user.id, file_name)
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/files/rename")
async def rename_file(
    request: Request,
    old_file_name: str,
    new_file_name: str,
    s3_service: S3Service = Depends(get_s3_service),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Переименовать файл для текущего пользователя"""
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)

    try:
        s3_service.rename_file(current_user.id, old_file_name, new_file_name)
        return {"message": "File renamed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/download")
async def download_file(
    request: Request,
    file_name: str,
    s3_service: S3Service = Depends(get_s3_service),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)

    try:
        file_data = s3_service.download_file(current_user.id, file_name)

        file_stream = BytesIO(file_data)

        return StreamingResponse(
            file_stream,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
