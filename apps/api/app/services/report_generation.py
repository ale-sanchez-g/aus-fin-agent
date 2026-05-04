import json
import os
from datetime import datetime, timezone
from typing import Optional

import structlog

from app.core.config import settings
from app.schemas.report import DiscoveryReport, ReportSection

log = structlog.get_logger()


class ReportGenerationService:
    def generate_report(
        self,
        session_id: str,
        user_intent: Optional[str],
        product_category: Optional[str],
        weight_profile: Optional[str],
        all_products: list[dict],
        eligible_products: list[dict],
        scored_products: list[dict],
        narrative: str,
        compliance_notes: list[str],
        ranking_metadata: Optional[dict] = None,
    ) -> DiscoveryReport:
        top_n = scored_products[:10]
        top_recommendations = []
        for rank, product in enumerate(top_n, start=1):
            top_recommendations.append(
                {
                    "rank": rank,
                    "product_id": product.get("id"),
                    "external_product_id": product.get("external_product_id"),
                    "name": product.get("name", "Unknown Product"),
                    "provider_id": product.get("provider_id"),
                    "brand": product.get("brand"),
                    "brand_name": product.get("brand_name"),
                    "provider_name": product.get("brand_name"),
                    "category": product.get("category"),
                    "total_score": product.get("total_score", 0.0),
                    "score_breakdown": product.get("score_breakdown", {}),
                    "fees": product.get("fees", []),
                    "rates": product.get("rates", []),
                    "features": product.get("features", []),
                    "application_uri": product.get("application_uri"),
                }
            )

        sections = [
            ReportSection(
                title="Executive Summary",
                content={
                    "intent": user_intent,
                    "category": product_category,
                    "products_evaluated": len(all_products),
                    "products_eligible": len(eligible_products),
                    "top_recommendation": top_recommendations[0] if top_recommendations else None,
                },
                section_type="summary",
            ),
            ReportSection(
                title="Methodology",
                content={
                    "weight_profile": weight_profile,
                    "scoring_dimensions": [
                        "monthly_fees",
                        "rate_competitiveness",
                        "feature_fit",
                        "eligibility_fit",
                        "digital_capability",
                        "suitability",
                    ],
                    "description": (
                        "Products are scored across six dimensions using a weighted scoring model. "
                        f"The '{weight_profile}' profile was applied to reflect stated priorities."
                    ),
                },
                section_type="methodology",
            ),
            ReportSection(
                title="Top Recommendations",
                content=top_recommendations,
                section_type="recommendations",
            ),
            ReportSection(
                title="Analysis Narrative",
                content=narrative,
                section_type="narrative",
            ),
            ReportSection(
                title="Compliance & Disclaimers",
                content={
                    "notes": compliance_notes,
                    "disclaimer": settings.DISCLAIMER_TEXT,
                },
                section_type="compliance",
            ),
        ]

        report_metadata = {
            "ranking": {
                "tie_diversification_applied": bool(
                    (ranking_metadata or {}).get("tie_diversification_applied", False)
                )
            }
        }

        return DiscoveryReport(
            session_id=session_id,
            generated_at=datetime.now(timezone.utc),
            product_category=product_category,
            user_intent=user_intent,
            total_products_evaluated=len(all_products),
            total_eligible_products=len(eligible_products),
            top_recommendations=top_recommendations,
            narrative=narrative,
            sections=sections,
            compliance_notes=compliance_notes,
            disclaimer=settings.DISCLAIMER_TEXT,
            weight_profile=weight_profile,
            metadata=report_metadata,
        )

    def persist_report(self, report: DiscoveryReport) -> tuple[Optional[str], Optional[str]]:
        """
        Persist report to S3 or local filesystem.
        Returns (s3_key, local_path).
        """
        report_dict = report.model_dump(mode="json")
        s3_key = None
        local_path = None

        # Try S3 first
        if settings.S3_REPORTS_BUCKET:
            try:
                import boto3

                s3 = boto3.client("s3", region_name=settings.AWS_REGION)
                key = f"reports/{report.session_id}/{report.generated_at.strftime('%Y%m%dT%H%M%S')}.json"
                s3.put_object(
                    Bucket=settings.S3_REPORTS_BUCKET,
                    Key=key,
                    Body=json.dumps(report_dict, default=str),
                    ContentType="application/json",
                )
                s3_key = key
                log.info("report_saved_s3", key=key, session_id=report.session_id)
            except Exception as exc:
                log.warning("s3_write_failed", error=str(exc))

        # Always write local copy as fallback
        try:
            reports_dir = "reports"
            os.makedirs(reports_dir, exist_ok=True)
            filename = f"{reports_dir}/{report.session_id}.json"
            with open(filename, "w") as f:
                json.dump(report_dict, f, default=str, indent=2)
            local_path = filename
            log.info("report_saved_local", path=filename, session_id=report.session_id)
        except Exception as exc:
            log.warning("local_write_failed", error=str(exc))

        return s3_key, local_path


report_service = ReportGenerationService()
