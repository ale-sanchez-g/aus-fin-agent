from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.discovery_session import DiscoverySession, RecommendationResult


class DiscoveryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(
        self,
        user_id: str,
        user_intent: str,
        product_category: str,
        preferences: dict,
        constraints: dict,
        weight_profile: str = "balanced",
        client_profile_id: Optional[str] = None,
    ) -> DiscoverySession:
        session = DiscoverySession(
            user_id=user_id,
            user_intent=user_intent,
            product_category=product_category,
            preferences=preferences,
            constraints=constraints,
            weight_profile=weight_profile,
            client_profile_id=client_profile_id,
            status="pending",
        )
        self.db.add(session)
        return session

    def get_session(self, session_id: str) -> Optional[DiscoverySession]:
        return (
            self.db.query(DiscoverySession)
            .filter(DiscoverySession.id == session_id)
            .first()
        )

    def list_sessions_for_user(self, user_id: str) -> list[DiscoverySession]:
        return (
            self.db.query(DiscoverySession)
            .filter(DiscoverySession.user_id == user_id)
            .order_by(DiscoverySession.created_at.desc())
            .all()
        )

    def update_session_status(
        self,
        session_id: str,
        status: str,
        error_message: Optional[str] = None,
        completed_at: Optional[datetime] = None,
    ):
        session = self.get_session(session_id)
        if session:
            session.status = status
            if error_message is not None:
                session.error_message = error_message
            if completed_at is not None:
                session.completed_at = completed_at

    def create_result(
        self,
        session_id: str,
        rank: int,
        total_score: float,
        product_id: Optional[str] = None,
        external_product_id: Optional[str] = None,
        score_breakdown: Optional[dict] = None,
        narrative: Optional[str] = None,
    ) -> RecommendationResult:
        result = RecommendationResult(
            session_id=session_id,
            product_id=product_id,
            external_product_id=external_product_id,
            rank=rank,
            total_score=total_score,
            score_breakdown=score_breakdown,
            narrative=narrative,
        )
        self.db.add(result)
        return result

    def get_results_for_session(self, session_id: str) -> list[RecommendationResult]:
        return (
            self.db.query(RecommendationResult)
            .filter(RecommendationResult.session_id == session_id)
            .order_by(RecommendationResult.rank)
            .all()
        )
