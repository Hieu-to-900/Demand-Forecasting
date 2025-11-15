"""Subgraph for Output and Recommendations - generates recommendations, alerts, and notifications.

This subgraph handles:
1. Analyze forecasts vs production capacity
2. Generate production suggestions
3. Generate risk alerts
4. Build notification messages
5. Send notifications (mock for now)
"""

from __future__ import annotations

from typing import Any, Dict, List

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

from agent.types_new import Context, State


async def analyze_forecast_vs_capacity(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Analyze forecasts against production capacity.
    
    Compares forecasted demand with available production capacity
    to identify bottlenecks and opportunities.
    """
    aggregated_forecasts = state.aggregated_forecasts or {}
    internal_data = state.aggregated_data.get("internal", {}) if state.aggregated_data else {}
    
    forecasts = aggregated_forecasts.get("forecasts", [])
    production_capacity = internal_data.get("production_capacity", {})
    
    # Analyze capacity vs demand
    total_forecast = aggregated_forecasts.get("total_forecast_units", 0)
    total_capacity = sum(line["max_monthly"] for line in production_capacity.values()) * 3  # 3 months (Q1)
    
    capacity_analysis = {
        "total_forecast_q1": total_forecast,
        "total_capacity_q1": total_capacity,
        "utilization_rate": total_forecast / total_capacity if total_capacity > 0 else 0,
        "capacity_status": "sufficient" if total_forecast < total_capacity * 0.85 else "constrained",
        "surplus_capacity": max(0, total_capacity - total_forecast),
        "shortfall": max(0, total_forecast - total_capacity),
    }
    
    return {
        "capacity_analysis": capacity_analysis,
    }


async def generate_production_suggestions(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Generate production planning suggestions based on forecasts.
    
    Provides actionable recommendations for production planning.
    """
    capacity_analysis = state.capacity_analysis or {}
    aggregated_forecasts = state.aggregated_forecasts or {}
    
    suggestions = []
    
    # Check capacity utilization
    utilization = capacity_analysis.get("utilization_rate", 0)
    
    if utilization > 0.9:
        suggestions.append({
            "priority": "high",
            "category": "capacity",
            "suggestion": "Consider adding overtime shifts or contracting with third-party manufacturers",
            "impact": "Critical for meeting Q1 demand"
        })
    elif utilization > 0.85:
        suggestions.append({
            "priority": "medium",
            "category": "capacity",
            "suggestion": "Plan for potential capacity constraints, prepare contingency production plans",
            "impact": "Moderate risk for Q1 delivery"
        })
    else:
        suggestions.append({
            "priority": "low",
            "category": "capacity",
            "suggestion": "Current capacity is sufficient, consider optimizing production scheduling",
            "impact": "Opportunity for efficiency improvements"
        })
    
    # Check inventory levels
    forecasts = aggregated_forecasts.get("forecasts", [])
    for forecast_item in forecasts[:3]:  # Top 3 products
        product_code = forecast_item.get("product_code")
        forecast_units = forecast_item.get("forecast", {}).get("forecast_units", 0)
        
        suggestions.append({
            "priority": "medium",
            "category": "inventory",
            "suggestion": f"Ensure {product_code} inventory covers {forecast_units} units forecast for Q1",
            "impact": "Maintain service level"
        })
    
    return {
        "production_suggestions": suggestions,
    }


async def generate_risk_alerts(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Generate risk alerts based on supply chain and capacity analysis.
    
    Identifies and prioritizes risks that need attention.
    """
    supply_chain_risks = state.aggregated_data.get("supply_chain", {}) if state.aggregated_data else {}
    capacity_analysis = state.capacity_analysis or {}
    
    alerts = []
    
    # Supply chain risk alerts
    overall_risk = supply_chain_risks.get("overall_risk_score", 0)
    if overall_risk > 0.3:
        alerts.append({
            "alert_type": "supply_chain_risk",
            "severity": "high" if overall_risk > 0.5 else "medium",
            "message": f"Supply chain risk score is {overall_risk:.2f}. Monitor supplier performance closely.",
            "action_required": "Review supplier contracts and backup plans",
            "timestamp": "2025-01-15T10:15:00"
        })
    
    # Capacity constraint alerts
    if capacity_analysis.get("capacity_status") == "constrained":
        shortfall = capacity_analysis.get("shortfall", 0)
        alerts.append({
            "alert_type": "capacity_constraint",
            "severity": "high",
            "message": f"Production capacity may fall short by {shortfall} units in Q1",
            "action_required": "Urgent: Arrange additional production capacity",
            "timestamp": "2025-01-15T10:15:00"
        })
    
    # Supplier-specific alerts
    supplier_status = supply_chain_risks.get("supplier_status", [])
    for supplier in supplier_status:
        if supplier.get("risk_level") == "high":
            alerts.append({
                "alert_type": "supplier_risk",
                "severity": "high",
                "message": f"Supplier {supplier.get('name')} has high risk level",
                "action_required": "Contact supplier and assess impact",
                "timestamp": "2025-01-15T10:15:00"
            })
    
    return {
        "alerts_triggered": alerts,
        "alert_summary": {
            "total_alerts": len(alerts),
            "high_severity": len([a for a in alerts if a.get("severity") == "high"]),
            "medium_severity": len([a for a in alerts if a.get("severity") == "medium"]),
        }
    }


async def build_notification_message(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Build notification messages for stakeholders.
    
    Formats forecasts, recommendations, and alerts into notification messages.
    """
    aggregated_forecasts = state.aggregated_forecasts or {}
    production_suggestions = state.production_suggestions or []
    alerts = state.alerts_triggered or []
    
    # Build summary message
    total_forecast = aggregated_forecasts.get("total_forecast_units", 0)
    total_products = aggregated_forecasts.get("total_products", 0)
    
    message = {
        "subject": "Q1 2025 Demand Forecast - Action Required",
        "summary": f"Forecast complete for {total_products} products. Total Q1 demand: {total_forecast:,} units.",
        "sections": [
            {
                "title": "Forecast Summary",
                "content": f"Total forecasted demand for Q1 2025: {total_forecast:,} units across {total_products} products."
            },
            {
                "title": "Key Recommendations",
                "content": [s.get("suggestion") for s in production_suggestions[:3]]
            },
            {
                "title": "Alerts Requiring Attention",
                "content": [a.get("message") for a in alerts if a.get("severity") == "high"]
            }
        ],
        "recipients": ["production_planning@denso.com", "supply_chain@denso.com"],
        "priority": "high" if any(a.get("severity") == "high" for a in alerts) else "normal",
        "timestamp": "2025-01-15T10:20:00"
    }
    
    return {
        "notification_message": message,
    }


async def send_notification(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Send notification to stakeholders.
    
    Phase 1: Mock/log notification
    Phase 2: Real email/Slack/Teams integration
    """
    notification_message = state.notification_message or {}
    
    # Mock notification sending
    print(f"\n{'='*60}")
    print(f"NOTIFICATION SENT")
    print(f"{'='*60}")
    print(f"To: {', '.join(notification_message.get('recipients', []))}")
    print(f"Subject: {notification_message.get('subject')}")
    print(f"Priority: {notification_message.get('priority')}")
    print(f"\n{notification_message.get('summary')}")
    print(f"{'='*60}\n")
    
    notification_status = {
        "sent": True,
        "recipients_count": len(notification_message.get("recipients", [])),
        "delivery_timestamp": "2025-01-15T10:20:00",
        "method": "mock",  # Will be "email", "slack", etc. in Phase 2
    }
    
    return {
        "notification_sent": True,
        "notification_status": notification_status,
    }


# Create Subgraph_Output
def create_output_subgraph() -> StateGraph:
    """Create the output and recommendations subgraph.
    
    Workflow:
    1. Analyze forecasts vs capacity
    2. Generate production suggestions (parallel)
    3. Generate risk alerts (parallel)
    4. Build notification message
    5. Send notification
    """
    subgraph = StateGraph(State, context_schema=Context)
    
    # Add nodes
    subgraph.add_node("analyze_capacity", analyze_forecast_vs_capacity)
    subgraph.add_node("generate_suggestions", generate_production_suggestions)
    subgraph.add_node("generate_alerts", generate_risk_alerts)
    subgraph.add_node("build_message", build_notification_message)
    subgraph.add_node("send_notification", send_notification)
    
    # Sequential flow
    subgraph.add_edge("__start__", "analyze_capacity")
    
    # Parallel generation of suggestions and alerts
    subgraph.add_edge("analyze_capacity", "generate_suggestions")
    subgraph.add_edge("analyze_capacity", "generate_alerts")
    
    # Both flow to message building
    subgraph.add_edge("generate_suggestions", "build_message")
    subgraph.add_edge("generate_alerts", "build_message")
    
    # Send notification
    subgraph.add_edge("build_message", "send_notification")
    
    return subgraph.compile(name="Subgraph_Output")


# Main function to run subgraph as a node
async def run_output_subgraph(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Run the output and recommendations subgraph as a single node."""
    subgraph = create_output_subgraph()
    result = await subgraph.ainvoke(state)
    return result
