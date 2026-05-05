from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes.intake_node import intake_node
from app.agents.nodes.retrieval_node import retrieval_node
from app.agents.nodes.eligibility_node import eligibility_node
from app.agents.nodes.scoring_node import scoring_node
from app.agents.nodes.reasoning_node import reasoning_node
from app.agents.nodes.compliance_node import compliance_node
from app.agents.nodes.report_node import report_node


def should_continue(state: AgentState) -> str:
    if state.get("error"):
        return "end"
    return "continue"


def build_discovery_graph():
    graph = StateGraph(AgentState)
    graph.add_node("intake", intake_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("eligibility", eligibility_node)
    graph.add_node("scoring", scoring_node)
    graph.add_node("reasoning", reasoning_node)
    graph.add_node("compliance", compliance_node)
    graph.add_node("report_gen", report_node)

    graph.set_entry_point("intake")
    graph.add_conditional_edges(
        "intake", should_continue, {"continue": "retrieval", "end": END}
    )
    graph.add_conditional_edges(
        "retrieval", should_continue, {"continue": "eligibility", "end": END}
    )
    graph.add_conditional_edges(
        "eligibility", should_continue, {"continue": "scoring", "end": END}
    )
    graph.add_conditional_edges(
        "scoring", should_continue, {"continue": "reasoning", "end": END}
    )
    graph.add_conditional_edges(
        "reasoning", should_continue, {"continue": "compliance", "end": END}
    )
    graph.add_edge("compliance", "report_gen")
    graph.add_edge("report_gen", END)

    return graph.compile()


discovery_graph = build_discovery_graph()
