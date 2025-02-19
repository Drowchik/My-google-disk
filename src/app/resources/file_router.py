from io import BytesIO
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query

from src.app.models import Folder, SharedAccess, User
from src.app.schemas.shemas import FolderCreateRequest, RenameFileRequest, ShareFolderRequest
from src.app.services.auth import AuthService, UserService
from src.app.core.database import get_auth_service, get_db, get_s3_service
from src.app.services.s3 import S3Service
from urllib.parse import quote

router = APIRouter(prefix="/mydisk", tags=["Загрузка файлов"],)


@router.post("/files/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    folder_path: str = Form(None),
    s3_service: S3Service = Depends(get_s3_service),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)

    try:
        file_data = await file.read()
        folder = folder_path or ""
        s3_service.upload_file(folder,
                               current_user.id, file.filename, file_data
                               )
        return {"message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
async def list_user_files(
    request: Request,
    path: str = Query("/", description="Путь до папки, например '/docs/'"),
    s3_service: S3Service = Depends(get_s3_service),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)
    try:
        files = s3_service.list_files(current_user.id)
        prefix = f"users/{current_user.id}/" if path == '/' else f"users/{current_user.id}/{path}"
        filtered_files = [
            file.replace(prefix, "")
            for file in files
            if file != prefix
            and file.startswith(prefix)
            and ("/" not in file.replace(prefix, "")[:-1] if file.replace(prefix, "") else True)
        ]
        return {"files": filtered_files}
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
    rename_file: RenameFileRequest,
    s3_service: S3Service = Depends(get_s3_service),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)

    try:
        s3_service.rename_file(
            current_user.id, rename_file.old_name, rename_file.new_name
        )
        return {"message": "File renamed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/download")
async def download_file(
    request: Request,
    file_name: str,
    generate_link: bool = False,
    s3_service: S3Service = Depends(get_s3_service),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)

    try:
        if generate_link:
            presigned_url = s3_service.generate_presigned_url(
                current_user.id, file_name)
            return {"download_link": presigned_url}

        file_data = s3_service.download_file(current_user.id, file_name)
        file_stream = BytesIO(file_data)
        encoded_file_name = quote(file_name)

        return StreamingResponse(
            file_stream,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_file_name}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/folders/share")
async def share_folder(
    request: Request,
    data: ShareFolderRequest,   # Почта пользователя
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Предоставление доступа к папке другому пользователю"""
    folder_path = data.folder_path
    user_email = data.user_email
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)

    # Получаем пользователя по почте
    user = await db.execute(select(User).filter(User.email == user_email))
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Находим папку по пути
    # Этот метод должен находить папку по пути
    path_name = f"users/{current_user.id}/{folder_path}"
    folder = await user_service.get_by_path(path_name)
    if not folder or folder.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No access to this folder")

    # Создаем запись о доступе
    shared_access = SharedAccess(
        folder_id=folder.id, user_id=user.id, permissions="permissions"
    )
    db.add(shared_access)
    await db.commit()

    return {"message": "Access granted successfully"}


@router.get("/folders/shared")
async def get_shared_folders(
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Получить список расшаренных папок для текущего пользователя"""
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)
    query = (
        select(Folder)
        .join(SharedAccess, SharedAccess.folder_id == Folder.id)
        .join(User, SharedAccess.user_id == User.id)
        .where(SharedAccess.user_id == current_user.id)
    )
    result = await db.execute(query)
    shared_folders = result.scalars().all()
    filtered_files = {
        "files": [file.name for file in shared_folders]
    }
    return [file.name for file in shared_folders]


@router.post("/folders")
async def create_folder(
    request: Request,
    folder_request: FolderCreateRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
    s3_service: S3Service = Depends(get_s3_service),
):
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)

    if not folder_request.name.strip():
        raise HTTPException(
            status_code=400, detail="Имя папки не может быть пустым")

    # Создаем новую папку в базе данных
    path_name = s3_service.get_user_folder(current_user.id)
    folder_name = f'{path_name}/{folder_request.path + folder_request.name}/'
    new_folder = Folder(
        name=folder_name,
        owner_id=current_user.id
    )
    db.add(new_folder)
    await db.commit()
    await db.refresh(new_folder)
    # Создаем папку в S3
    path_name = s3_service.get_user_folder(current_user.id)
    s3_service.create_folder(folder_name)
    # Возвращаем информацию о созданной папке
    return {"id": new_folder.id, "name": new_folder.name, "owner_id": new_folder.owner_id}


@router.delete("/folders")
async def delete_folder(
    request: Request,
    path: str,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
    s3_service: S3Service = Depends(get_s3_service),
):
    user_service = UserService(db, auth_service)
    current_user = await user_service.get_current_user(request)
    path_name = s3_service.get_user_folder(current_user.id)
    folder_name = f'{path_name}/{path}'
    # Проверяем существование папки
    folder = await db.execute(
        select(Folder).where(Folder.name == folder_name,
                             Folder.owner_id == current_user.id)
    )
    folder = folder.scalars().first()

    if not folder:
        raise HTTPException(status_code=404, detail="Папка не найдена")

    # Удаляем папку из базы данных
    await db.delete(folder)
    await db.commit()

    # Удаляем папку из S3
    s3_service.delete_folder(current_user.id, folder_name)

    return {"detail": "Папка успешно удалена"}


@router.get("/files/shared")
async def list_shared_files(
    path: str = Query("/", description="Путь до папки, например '/docs/'"),
    s3_service: S3Service = Depends(get_s3_service),
):

    path = path[1:-1]
    try:

        filtered_files = [
            file.replace(path, "") for file in s3_service.list_files_shared(path) if file != path
        ]
        return filtered_files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
