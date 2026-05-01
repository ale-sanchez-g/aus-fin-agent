import re
import structlog
from app.agents.state import AgentState
from app.core.config import settings

log = structlog.get_logger()

# Prescriptive language patterns to soften
_PRESCRIPTIVE_PATTERNS = [
    (r"\byou should\b", "you may wish to consider"),
    (r"\byou must\b", "it is noted that"),
    (r"\bwe recommend\b", "the discovery results suggest"),
    (r"\bI recommend\b", "the discovery results suggest"),
    (r"\bbest product for you\b", "a highly-scored product for your criteria"),
    (r"\bperfect for you\b", "well-matched to your stated criteria"),
    (r"\bguaranteed\b", "subject to provider terms"),
]

CDR_COMPLIANCE_NOTES = [
    "Product information is sourced from the Australian Consumer Data Right (CDR) open banking registry.",
    "Rates and fees are indicative and subject to change without notice.",
    "Eligibility criteria apply; verify with the product provider before applying.",
    "This discovery output does not constitute personal financial advice under the Corporations Act 2001 (Cth).",
    "AFS licensing obligations apply. This platform operates under a discovery/comparison service model only.",
]


def _strip_prescriptive_language(text: str) -> str:
    for pattern, replacement in _PRESCRIPTIVE_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def compliance_node(state: AgentState) -> dict:
    log.info("compliance_node", session_id=state.get("session_id"))
    try:
        narrative = state.get("narrative", "")

        # Soften any prescriptive language in the narrative
        compliant_narrative = _strip_prescriptive_language(narrative)

        # Build compliance notes
        compliance_notes = list(CDR_COMPLIANCE_NOTES)

        # Add feature-flag note if consented data mode is off
        if not settings.FEATURE_FLAG_CONSENTED_DATA_MODE:
            compliance_notes.append(
                "Analysis is based on publicly available CDR product data only. "
                "Consented personal data has not been used in this discovery session."
            )

        # Add disclaimer
        compliance_notes.append(settings.DISCLAIMER_TEXT)

        return {
            **state,
            "narrative": compliant_narrative,
            "compliance_notes": compliance_notes,
            "status": "compliance_complete",
        }
    except Exception as exc:
        log.error("compliance_node_error", error=str(exc))
        return {**state, "compliance_notes": [settings.DISCLAIMER_TEXT], "status": "compliance_complete"}
