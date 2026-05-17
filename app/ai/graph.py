"""
LangGraph agent graph for the AI e-commerce support chatbot.

Flow:
  START
    → intent_router
    → [conditional] one of:
        order_tracking_node
        return_refund_node
        payment_issue_node
        delivery_update_node
        product_recommendation_node
        faq_node
        escalate_node
        fallback_node
    → END
"""
from __future__ import annotations

from langgraph.graph import StateGraph, END, START

from app.ai.state import AgentState
from app.ai.node import (
    return_refund_node,
    payment_issue_node,
    delivery_update_node,
    product_recommendation_node,
    escalate_node,
    fallback_node,
)
from app.ai.nodes.intent_node import intent_router_node
from app.ai.nodes.faq_node import faq_node
from app.ai.nodes.order_track import order_tracking_node

# ── Routing function (pure — reads intent from state) ─────────────────────────
def route_by_intent(state: AgentState) -> str:
    """Return the name of the next node based on detected intent."""
    routing_map = {
        "order_tracking":          "order_tracking",
        "return_refund":           "return_refund",
        "payment_issue":           "payment_issue",
        "delivery_update":         "delivery_update",
        "product_recommendation":  "product_recommendation",
        "faq":                     "faq",
        "escalate_human":          "escalate",
        "out_of_scope":            "fallback",
    }
    return routing_map.get(state.intent or "out_of_scope", "fallback")


# ── Build the graph ────────────────────────────────────────────────────────────
def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("intent_router",         intent_router_node)
    graph.add_node("order_tracking",        order_tracking_node)
    graph.add_node("return_refund",         return_refund_node)
    graph.add_node("payment_issue",         payment_issue_node)
    graph.add_node("delivery_update",       delivery_update_node)
    graph.add_node("product_recommendation",product_recommendation_node)
    graph.add_node("faq",                   faq_node)
    graph.add_node("escalate",              escalate_node)
    graph.add_node("fallback",              fallback_node)

    # Entry → intent classification
    graph.add_edge(START,              "intent_router")

    # Intent router → conditional branch
    graph.add_conditional_edges(
        "intent_router",
        route_by_intent,
        {
            "order_tracking":          "order_tracking",
            "return_refund":           "return_refund",
            "payment_issue":           "payment_issue",
            "delivery_update":         "delivery_update",
            "product_recommendation":  "product_recommendation",
            "faq":                     "faq",
            "escalate":                "escalate",
            "fallback":                "fallback",
        },
    )

    # All leaf nodes → END
    for leaf in [
        "order_tracking", "return_refund", "payment_issue",
        "delivery_update", "product_recommendation", "faq",
        "escalate", "fallback",
    ]:
        graph.add_edge(leaf, END)

    return graph.compile()


# Singleton compiled graph — import this everywhere
agent = build_agent_graph()