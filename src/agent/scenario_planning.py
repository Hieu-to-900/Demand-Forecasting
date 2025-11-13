"""Scenario planning for demand forecasting."""

from __future__ import annotations

from typing import Any, Dict

from langchain_openai import ChatOpenAI
from langgraph.runtime import Runtime

from agent.types import Context, State


async def generate_scenarios(
    state: State,
    runtime: Runtime[Context],
    num_scenarios: int = 3,
) -> Dict[str, Any]:
    """Generate multiple demand forecast scenarios.

    Args:
        state: Current state with base forecast
        runtime: Runtime context
        num_scenarios: Number of scenarios to generate (optimistic, realistic, pessimistic)

    Returns:
        Dictionary with scenario analysis
    """
    seasonal_forecast = getattr(state, "seasonal_forecast", None)
    if not seasonal_forecast or "forecast_values" not in seasonal_forecast:
        return {
            "scenario_planning": {
                "error": "Base forecast required for scenario planning",
            }
        }

    base_forecast = seasonal_forecast["forecast_values"]
    forecast_dates = seasonal_forecast.get("forecast_dates", [])

    # Generate scenarios with different multipliers
    scenarios = {
        "optimistic": {
            "multiplier": 1.2,
            "description": "Best case: Strong market conditions, successful promotions, minimal competition",
            "probability": 0.2,
        },
        "realistic": {
            "multiplier": 1.0,
            "description": "Base case: Normal market conditions, expected trends continue",
            "probability": 0.5,
        },
        "pessimistic": {
            "multiplier": 0.8,
            "description": "Worst case: Economic downturn, increased competition, supply issues",
            "probability": 0.3,
        },
    }

    # Generate forecast for each scenario
    scenario_forecasts = {}
    for scenario_name, scenario_params in scenarios.items():
        multiplier = scenario_params["multiplier"]
        scenario_forecasts[scenario_name] = [
            round(float(v * multiplier), 2) for v in base_forecast
        ]

    # Calculate expected value (weighted average)
    expected_forecast = []
    for i in range(len(base_forecast)):
        expected = (
            scenario_forecasts["optimistic"][i] * scenarios["optimistic"]["probability"]
            + scenario_forecasts["realistic"][i] * scenarios["realistic"]["probability"]
            + scenario_forecasts["pessimistic"][i] * scenarios["pessimistic"]["probability"]
        )
        expected_forecast.append(round(float(expected), 2))

    # Use LLM for scenario analysis
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = f"""
    Analyze the following demand forecast scenarios:

    Optimistic Scenario (20% probability):
    - {scenarios['optimistic']['description']}
    - Forecast: {scenario_forecasts['optimistic'][:5]}... (showing first 5 days)

    Realistic Scenario (50% probability):
    - {scenarios['realistic']['description']}
    - Forecast: {scenario_forecasts['realistic'][:5]}... (showing first 5 days)

    Pessimistic Scenario (30% probability):
    - {scenarios['pessimistic']['description']}
    - Forecast: {scenario_forecasts['pessimistic'][:5]}... (showing first 5 days)

    Provide:
    1. Key differences between scenarios
    2. Risk factors to monitor
    3. Recommended actions for each scenario
    4. Contingency planning recommendations
    """

    try:
        response = llm.invoke(prompt)
        analysis = response.content if hasattr(response, "content") else str(response)

        scenario_results = {
            "scenarios": {
                name: {
                    "forecast": forecast,
                    "description": params["description"],
                    "probability": params["probability"],
                    "multiplier": params["multiplier"],
                }
                for name, forecast, params in zip(
                    scenarios.keys(),
                    scenario_forecasts.values(),
                    scenarios.values(),
                )
            },
            "expected_forecast": expected_forecast,
            "forecast_dates": forecast_dates,
            "llm_analysis": analysis[:500],
            "recommendations": [
                "Plan inventory for realistic scenario, with buffer for optimistic",
                "Maintain flexibility to scale up or down based on actual performance",
                "Monitor key indicators to identify which scenario is unfolding",
                "Prepare contingency plans for pessimistic scenario",
            ],
        }

        return {"scenario_planning": scenario_results}

    except Exception as e:
        # Fallback without LLM
        return {
            "scenario_planning": {
                "scenarios": {
                    name: {
                        "forecast": forecast,
                        "description": params["description"],
                        "probability": params["probability"],
                        "multiplier": params["multiplier"],
                    }
                    for name, forecast, params in zip(
                        scenarios.keys(),
                        scenario_forecasts.values(),
                        scenarios.values(),
                    )
                },
                "expected_forecast": expected_forecast,
                "forecast_dates": forecast_dates,
                "error": f"LLM analysis failed: {str(e)}",
                "recommendations": [
                    "Use expected forecast for planning",
                    "Maintain inventory flexibility",
                ],
            }
        }

