from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
import uuid


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column()

    # Связь с папками пользователя
    folders: Mapped[list["Folder"]] = relationship(
        "Folder", back_populates="owner", cascade="all, delete-orphan"
    )

    # Связь с доступами (когда пользователь имеет доступ к чужим папкам)
    shared_access: Mapped[list["SharedAccess"]] = relationship(
        "SharedAccess", back_populates="user"
    )


class Folder(Base):
    __tablename__ = "folders"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(nullable=False)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    # Связь с владельцем папки
    owner: Mapped["User"] = relationship(back_populates="folders")

    # Связь с доступами для других пользователей
    shared_users: Mapped[list["SharedAccess"]] = relationship(
        "SharedAccess", back_populates="folder"
    )


class SharedAccess(Base):
    __tablename__ = "shared_access"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    folder_id: Mapped[UUID] = mapped_column(
        ForeignKey("folders.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    permissions: Mapped[str] = mapped_column(nullable=False)

    # Связь с папкой
    folder: Mapped["Folder"] = relationship(back_populates="shared_users")

    # Связь с пользователем, которому предоставлен доступ
    user: Mapped["User"] = relationship(back_populates="shared_access")
