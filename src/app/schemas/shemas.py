from pydantic import BaseModel, EmailStr
from datetime import date


class SUserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class SUserOutput(BaseModel):
    name: str
    email: str


class SUserLogin(BaseModel):
    email: EmailStr
    password: str


class RenameFileRequest(BaseModel):
    old_name: str
    new_name: str


class FolderCreateRequest(BaseModel):
    name: str
    path: str


class ShareFolderRequest(BaseModel):
    folder_path: str
    user_email: str
