import structlog
from app.agents.state import AgentState
from app.services.report_generation import report_service

log = structlog.get_logger()


def report_node(state: AgentState) -> dict:
    log.info("report_node", session_id=state.get("session_id"))
    try:
        report = report_service.generate_report(
            session_id=state["session_id"],
            user_intent=state.get("user_intent"),
            product_category=state.get("product_category"),
            weight_profile=state.get("weight_profile"),
            all_products=state.get("products") or [],
            eligible_products=state.get("eligible_products") or [],
            scored_products=state.get("scored_products") or [],
            narrative=state.get("narrative", ""),
            compliance_notes=state.get("compliance_notes") or [],
        )

        # Persist report
        s3_key, local_path = report_service.persist_report(report)

        # Store report artifact in DB
        try:
            from app.db.session import SessionLocal
            from app.repositories.report_repository import ReportRepository

            db = SessionLocal()
            try:
                repo = ReportRepository(db)
                artifact = repo.create_artifact(
                    session_id=state["session_id"],
                    content=report.model_dump(mode="json"),
                    s3_key=s3_key,
                    local_path=local_path,
                )
                db.commit()
                log.info("report_artifact_created", artifact_id=artifact.id)
            finally:
                db.close()
        except Exception as exc:
            log.warning("report_artifact_save_failed", error=str(exc))

        report_dict = report.model_dump(mode="json")
        return {**state, "report": report_dict, "status": "completed"}

    except Exception as exc:
        log.error("report_node_error", error=str(exc))
        return {**state, "report": {}, "error": f"Report generation failed: {exc}", "status": "failed"}
