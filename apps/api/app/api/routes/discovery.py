import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.security import get_current_user, CurrentUser
from app.repositories.discovery_repository import DiscoveryRepository
from app.schemas.discovery import (
    CreateDiscoveryRequest,
    DiscoverySessionResponse,
    RecommendationResultResponse,
)
import structlog

log = structlog.get_logger()
router = APIRouter()


def _run_discovery_workflow(session_id: str, state: dict):
    """Run the discovery agent graph in a background thread."""
    try:
        from app.agents.graph import discovery_graph
        from app.db.session import SessionLocal
        from app.repositories.discovery_repository import DiscoveryRepository
        from datetime import datetime, timezone

        result = discovery_graph.invoke(state)

        db = SessionLocal()
        try:
            repo = DiscoveryRepository(db)
            status = "completed" if not result.get("error") else "failed"
            repo.update_session_status(
                session_id=session_id,
                status=status,
                error_message=result.get("error"),
                completed_at=datetime.now(timezone.utc),
            )
            if result.get("scored_products"):
                for rank, scored in enumerate(result["scored_products"][:10], start=1):
                    breakdown = scored.get("score_breakdown", {})
                    repo.create_result(
                        session_id=session_id,
                        product_id=scored.get("id"),
                        external_product_id=scored.get("external_product_id"),
                        rank=rank,
                        total_score=scored.get("total_score", 0.0),
                        score_breakdown=breakdown,
                        narrative=result.get("narrative", ""),
                    )
            db.commit()
        finally:
            db.close()
    except Exception as exc:
        log.error("discovery_workflow_error", session_id=session_id, error=str(exc))
        try:
            from app.db.session import SessionLocal
            from app.repositories.discovery_repository import DiscoveryRepository

            db = SessionLocal()
            try:
                repo = DiscoveryRepository(db)
                repo.update_session_status(session_id=session_id, status="failed", error_message=str(exc))
                db.commit()
            finally:
                db.close()
        except Exception:
            pass


@router.post("/sessions", response_model=DiscoverySessionResponse, status_code=201)
async def create_discovery_session(
    request: CreateDiscoveryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    repo = DiscoveryRepository(db)
    session = repo.create_session(
        user_id=current_user.user_id,
        user_intent=request.user_intent,
        product_category=request.product_category or "TRANS_AND_SAVINGS_ACCOUNTS",
        preferences=request.preferences or {},
        constraints=request.constraints or {},
        weight_profile=request.weight_profile or "balanced",
        client_profile_id=request.client_profile_id,
    )
    db.commit()
    db.refresh(session)

    agent_state = {
        "session_id": session.id,
        "user_intent": request.user_intent,
        "product_category": session.product_category,
        "preferences": request.preferences or {},
        "constraints": request.constraints or {},
        "weight_profile": request.weight_profile or "balanced",
        "products": [],
        "eligible_products": [],
        "scored_products": [],
        "narrative": "",
        "compliance_notes": [],
        "report": {},
        "error": None,
        "status": "running",
    }

    background_tasks.add_task(_run_discovery_workflow, session.id, agent_state)

    return session


@router.get("/sessions", response_model=List[DiscoverySessionResponse])
async def list_sessions(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    repo = DiscoveryRepository(db)
    return repo.list_sessions_for_user(current_user.user_id)


@router.get("/sessions/{session_id}", response_model=DiscoverySessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    repo = DiscoveryRepository(db)
    session = repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/sessions/{session_id}/results", response_model=List[RecommendationResultResponse])
async def get_session_results(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    repo = DiscoveryRepository(db)
    session = repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return repo.get_results_for_session(session_id)
