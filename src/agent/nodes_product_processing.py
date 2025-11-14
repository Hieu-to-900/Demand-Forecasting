"""Nodes for product batch processing and forecasting."""

from __future__ import annotations

from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.internal_data_mock import (
    get_all_product_codes,
    get_internal_data_for_product,
    get_historical_sales_array,
    get_inventory_level,
    get_production_plans_array,
)
from agent.types_new import Context, State


async def split_product_batches(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Split products into batches for parallel processing.

    Input: List of product codes
    Output: Batches of product codes (5 batches)

    Purpose: Divide products into batches for parallel processing.
    """
    # Get product codes from state or context
    product_codes = state.product_codes or []

    if not product_codes:
        # Use mock product codes from internal_data_mock if none provided
        product_codes = get_all_product_codes()  # Returns 5 products: INV-001 to INV-005

    # Split into 5 batches
    batch_size = len(product_codes) // 5
    if batch_size == 0:
        batch_size = 1

    batches = []
    for i in range(5):
        start_idx = i * batch_size
        end_idx = start_idx + batch_size if i < 4 else len(product_codes)
        batch = product_codes[start_idx:end_idx]
        if batch:
            batches.append(batch)

    return {
        "product_batches": batches,
        "total_batches": len(batches),
        "total_products": len(product_codes),
    }


async def retrieve_relevant_context(
    product_code: str,
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Retrieve relevant context from ChromaDB for a product.

    Input: Product code
    Output: Top-N relevant external insights

    Purpose: Query ChromaDB to get top-N relevant external insights (e.g., "EV sales up 25% in EU").
    """
    # Mock ChromaDB query - replace with actual ChromaDB query
    # In real implementation, would:
    # 1. Generate query embedding for product_code
    # 2. Query ChromaDB collection
    # 3. Retrieve top-N similar documents

    relevant_insights = [
        {
            "content": "EV sales up 25% in EU - relevant for automotive components",
            "relevance_score": 0.85,
            "source": "IEA",
            "timestamp": "2024-10-01",
        },
        {
            "content": "Battery demand +18% due to subsidies",
            "relevance_score": 0.78,
            "source": "EV Volumes",
            "timestamp": "2024-10-05",
        },
    ]

    return {
        "product_code": product_code,
        "relevant_context": relevant_insights,
        "context_count": len(relevant_insights),
    }


async def analyze_with_api(
    product_code: str,
    relevant_context: list[Dict[str, Any]],
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Analyze retrieved context with xAI API.

    Input: Product code, relevant context
    Output: Market insight (anonymized)

    Purpose: Send retrieved public context to xAI (anonymized) to generate market insight.
    """
    # Mock xAI API call - replace with actual xAI API integration
    # In real implementation, would:
    # 1. Anonymize context (remove sensitive info)
    # 2. Call xAI API
    # 3. Get market insight

    context_summary = " ".join([item["content"] for item in relevant_context[:3]])

    # Mock insight generation
    market_insight = {
        "product_code": product_code,
        "insight": f"Market analysis for {product_code}: {context_summary[:100]}...",
        "key_findings": [
            "EV market growth trend detected",
            "Battery component demand increasing",
            "Regional variations in demand patterns",
        ],
        "confidence": 0.82,
        "analysis_timestamp": "2024-10-15T10:10:00",
    }

    return {
        "product_code": product_code,
        "market_insight": market_insight,
    }


async def fuse_with_internal_data(
    product_code: str,
    market_insight: Dict[str, Any],
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Fuse public insight with internal data.

    Input: Product code, market insight, internal data
    Output: Combined dataset ready for forecasting

    Purpose: Combine public insight with local historical sales, inventory, and production plans.
    """
    try:
        # Get comprehensive internal data from mock database
        product_data = get_internal_data_for_product(product_code)
        
        # Extract key metrics
        historical_sales = get_historical_sales_array(product_code, periods=5)
        inventory_info = product_data["inventory_levels"]
        
        internal_data = {
            "product_code": product_code,
            "product_name": product_data["product_name"],
            "category": product_data["category"],
            "subcategory": product_data["subcategory"],
            "unit_price": product_data["unit_price"],
            "product_lifecycle": product_data["product_lifecycle"],
            "manufacturing_location": product_data["manufacturing_location"],
            
            # Historical sales (last 5 months)
            "historical_sales": historical_sales,
            "historical_sales_full": product_data["historical_sales"],  # All 36 months
            
            # Inventory
            "inventory_levels": inventory_info["current_stock"],
            "safety_stock": inventory_info["safety_stock"],
            "reorder_point": inventory_info["reorder_point"],
            "max_stock": inventory_info["max_stock"],
            "stock_status": inventory_info["stock_status"],
            "warehouse_location": inventory_info["warehouse_location"],
            "lead_time_days": inventory_info["lead_time_days"],
            
            # Production plans
            "production_plans": get_production_plans_array(product_code),
            "production_plans_full": product_data["production_plans"],
            
            # Quality metrics
            "quality_metrics": product_data["quality_metrics"],
            
            # Market segments and regions
            "market_segments": product_data["market_segments"],
            "regions": product_data["regions"],
        }
        
        # Calculate historical trend
        if len(historical_sales) >= 2:
            recent_avg = sum(historical_sales[-3:]) / min(3, len(historical_sales))
            older_avg = sum(historical_sales[:2]) / min(2, len(historical_sales))
            if recent_avg > older_avg * 1.05:
                historical_trend = "increasing"
            elif recent_avg < older_avg * 0.95:
                historical_trend = "decreasing"
            else:
                historical_trend = "stable"
        else:
            historical_trend = "stable"
        
    except ValueError:
        # Fallback to simple mock data if product not found
        internal_data = {
            "product_code": product_code,
            "product_name": f"Product {product_code}",
            "historical_sales": [100, 120, 115, 130, 125],
            "inventory_levels": 500,
            "production_plans": [150, 160, 155],
            "stock_status": "adequate",
            "product_lifecycle": "unknown",
        }
        historical_trend = "stable"
    
    # Fuse with market insight
    fused_data = {
        "product_code": product_code,
        "internal_data": internal_data,
        "market_insight": market_insight,
        "combined_features": {
            "historical_trend": historical_trend,
            "market_signal": market_insight.get("key_findings", []),
            "inventory_status": internal_data.get("stock_status", "unknown"),
            "product_lifecycle": internal_data.get("product_lifecycle", "unknown"),
        },
    }

    return {
        "product_code": product_code,
        "fused_data": fused_data,
    }


async def generate_forecast(
    product_code: str,
    fused_data: Dict[str, Any],
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Generate demand forecast using ML model.

    Input: Product code, fused data
    Output: Forecast (units) for next quarter

    Purpose: Run local ML model (e.g., Prophet, LSTM) or rule-based adjustment to predict demand.
    """
    # Mock forecast generation - replace with actual Prophet/LSTM model
    # In real implementation, would:
    # 1. Prepare features from fused_data
    # 2. Run Prophet/LSTM model
    # 3. Generate forecast for next quarter

    historical_sales = fused_data["internal_data"]["historical_sales"]
    avg_sales = sum(historical_sales) / len(historical_sales)

    # Simple forecast with market adjustment
    market_factor = 1.15 if "increasing" in str(fused_data["combined_features"]["market_signal"]) else 1.0
    forecast_units = int(avg_sales * market_factor * 90)  # 90 days in quarter

    forecast = {
        "product_code": product_code,
        "forecast_period": "Q1_2025",
        "forecast_units": forecast_units,
        "confidence_interval": {
            "lower": int(forecast_units * 0.85),
            "upper": int(forecast_units * 1.15),
        },
        "method": "prophet_with_market_adjustment",
        "forecast_timestamp": "2024-10-15T10:15:00",
    }

    return {
        "product_code": product_code,
        "forecast": forecast,
    }


async def process_product_batch(
    batch_index: int,
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Process a batch of products (Retrieve → Analyze → Fuse → Forecast).

    Input: Batch index, product batch
    Output: Forecasts for all products in batch

    Purpose: Complete processing pipeline for a batch of products.
    """
    batches = state.product_batches or []
    if batch_index >= len(batches):
        return {"batch_results": []}

    product_batch = batches[batch_index]
    batch_results = []

    for product_code in product_batch:
        # Step 1: Retrieve relevant context
        context_result = await retrieve_relevant_context(product_code, state, runtime)
        relevant_context = context_result.get("relevant_context", [])

        # Step 2: Analyze with API
        analysis_result = await analyze_with_api(product_code, relevant_context, state, runtime)
        market_insight = analysis_result.get("market_insight", {})

        # Step 3: Fuse with internal data
        fuse_result = await fuse_with_internal_data(product_code, market_insight, state, runtime)
        fused_data = fuse_result.get("fused_data", {})

        # Step 4: Generate forecast
        forecast_result = await generate_forecast(product_code, fused_data, state, runtime)
        forecast = forecast_result.get("forecast", {})

        batch_results.append({
            "product_code": product_code,
            "forecast": forecast,
        })

    return {
        "batch_index": batch_index,
        "batch_results": batch_results,
        "products_processed": len(batch_results),
    }

