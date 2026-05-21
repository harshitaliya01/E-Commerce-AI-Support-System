from langgraph.graph import StateGraph, END, START
from app.ai.state import AgentState
from app.ai.nodes.unknow_node import unknown_node
from app.ai.nodes.intent_node import intent_router_node
from app.ai.nodes.return_refund import return_refund_node
from app.ai.nodes.payment_node import payment_issue_node
from app.ai.nodes.faq_node import faq_node
from app.ai.nodes.order_track import order_tracking_node

# ── Routing function (pure — reads intent from state) ─────────────────────────
def route_by_intent(state: AgentState) -> str:
    """Return the name of the next node based on detected intent."""
    routing_map = {
        "order_tracking":          "order_tracking",
        "return_refund":           "return_refund",
        "payment_issue":           "payment_issue",
        "faq":                     "faq",
        "unknown":                "unknown"
    }
    return routing_map.get(state.intent, "unknown")

# ── Build the graph ────────────────────────────────────────────────────────────
def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("intent_router",         intent_router_node)
    graph.add_node("order_tracking",        order_tracking_node)
    graph.add_node("return_refund",         return_refund_node)
    graph.add_node("payment_issue",         payment_issue_node)
    graph.add_node("faq",                   faq_node)
    graph.add_node("unknown",              unknown_node)


    graph.add_edge(START, "intent_router")

    graph.add_conditional_edges("intent_router",
        route_by_intent,
        {
            "order_tracking":"order_tracking",
            "return_refund":"return_refund",
            "payment_issue":"payment_issue",
            "faq":"faq",
            "unknown":"unknown",
        },
    )

    # All leaf nodes → END
    for leaf in ["order_tracking", "return_refund", "payment_issue", "faq", "unknown"]:
        graph.add_edge(leaf, END)

    return graph.compile()

agent = build_agent_graph()