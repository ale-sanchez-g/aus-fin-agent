from typing import Optional
from sqlalchemy.orm import Session

from app.models.report import ReportArtifact


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_artifact(
        self,
        session_id: str,
        content: Optional[dict] = None,
        s3_key: Optional[str] = None,
        local_path: Optional[str] = None,
        report_type: str = "discovery",
        format: str = "json",
    ) -> ReportArtifact:
        artifact = ReportArtifact(
            session_id=session_id,
            content=content,
            s3_key=s3_key,
            local_path=local_path,
            report_type=report_type,
            format=format,
        )
        self.db.add(artifact)
        return artifact

    def get_by_id(self, report_id: str) -> Optional[ReportArtifact]:
        return self.db.query(ReportArtifact).filter(ReportArtifact.id == report_id).first()

    def get_latest_for_session(self, session_id: str) -> Optional[ReportArtifact]:
        return (
            self.db.query(ReportArtifact)
            .filter(ReportArtifact.session_id == session_id)
            .order_by(ReportArtifact.created_at.desc())
            .first()
        )

    def list_for_session(self, session_id: str) -> list[ReportArtifact]:
        return (
            self.db.query(ReportArtifact)
            .filter(ReportArtifact.session_id == session_id)
            .order_by(ReportArtifact.created_at.desc())
            .all()
        )
