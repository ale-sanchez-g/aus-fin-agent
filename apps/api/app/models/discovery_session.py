import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, ForeignKey, Integer, Float, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class DiscoverySession(Base):
    __tablename__ = "discovery_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    client_profile_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("client_profiles.id"), nullable=True
    )
    user_intent: Mapped[str | None] = mapped_column(Text, nullable=True)
    product_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    constraints: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    weight_profile: Mapped[str | None] = mapped_column(String(50), nullable=True, default="balanced")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    results: Mapped[list["RecommendationResult"]] = relationship(
        "RecommendationResult", back_populates="session", cascade="all, delete-orphan"
    )
    report_artifacts: Mapped[list["ReportArtifact"]] = relationship(  # noqa: F821
        "ReportArtifact", back_populates="session", cascade="all, delete-orphan"
    )


class RecommendationResult(Base):
    __tablename__ = "recommendation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("discovery_sessions.id"), nullable=False
    )
    product_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("products.id"), nullable=True
    )
    external_product_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    score_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["DiscoverySession"] = relationship("DiscoverySession", back_populates="results")
