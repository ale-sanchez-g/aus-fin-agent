import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class ReportArtifact(Base):
    __tablename__ = "report_artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("discovery_sessions.id"), nullable=False
    )
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, default="discovery")
    s3_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    local_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    format: Mapped[str] = mapped_column(String(20), nullable=False, default="json")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    session: Mapped["DiscoverySession"] = relationship(  # noqa: F821
        "DiscoverySession", back_populates="report_artifacts"
    )
