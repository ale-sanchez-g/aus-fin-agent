from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user, CurrentUser
from app.repositories.report_repository import ReportRepository
from app.schemas.report import ReportArtifactResponse, DownloadUrlResponse
import structlog

log = structlog.get_logger()
router = APIRouter()


@router.get("/{session_id}", response_model=ReportArtifactResponse)
async def get_report(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    repo = ReportRepository(db)
    artifact = repo.get_latest_for_session(session_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Report not found for session")
    return artifact


@router.get("/download/{report_id}", response_model=DownloadUrlResponse)
async def get_download_url(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    repo = ReportRepository(db)
    artifact = repo.get_by_id(report_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Report not found")

    # Try S3 presigned URL first
    if artifact.s3_key:
        try:
            import boto3
            from app.core.config import settings

            s3 = boto3.client("s3", region_name=settings.AWS_REGION)
            url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.S3_REPORTS_BUCKET, "Key": artifact.s3_key},
                ExpiresIn=3600,
            )
            return DownloadUrlResponse(url=url, expires_in_seconds=3600, report_id=report_id)
        except Exception as e:
            log.warning("s3_presign_failed", error=str(e))

    # Fall back to local path or inline content URL
    if artifact.local_path:
        return DownloadUrlResponse(
            url=f"/api/v1/reports/file/{report_id}",
            expires_in_seconds=3600,
            report_id=report_id,
        )

    raise HTTPException(status_code=404, detail="Report file not available")
