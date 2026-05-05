import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class ClientProfile(Base):
    __tablename__ = "client_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    product_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    constraints: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
