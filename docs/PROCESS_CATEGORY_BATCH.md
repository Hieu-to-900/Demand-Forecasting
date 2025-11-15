# Workflow đầy đủ trong process_category_batch:

For each category (Spark Plugs hoặc AC System):
```
1. retrieve_category_context() ← BẠN NÓI ĐÚNG
   ├─ Query: f"{category} automotive market trends"
   ├─ ChromaDB: Tìm top-5 external market insights
   └─ Output: Category-level context (SHARED cho toàn bộ products)

2. analyze_category_with_api() ← BẠN NÓI ĐÚNG
   ├─ Input: Category context từ bước 1
   ├─ xAI API call: Phân tích market insights cho category
   └─ Output: Category-level market insight (SHARED)

3. For each product in category: ← BẠN THIẾU BƯỚC NÀY!
   
   3a. fuse_with_internal_data()
       ├─ Input: Product code + Category insight (shared)
       ├─ Get: Internal data (sales, inventory, capacity)
       └─ Output: Fused data = Internal + External insights
   
   3b. generate_forecast() ← BẠN NÓI ĐÚNG
       ├─ Input: Fused data (36 months historical sales)
       ├─ Prophet Model: Time-series forecasting
       ├─ Apply: Market adjustment từ category insight
       └─ Output: Forecast Q1 2025 (next 3 months)

4. Return: All forecasts for category
```

## 📊 Chi tiết từng bước:
Bước 1: retrieve_category_context (Category-level)

```
# 1 lần cho toàn bộ category
category_context = await retrieve_category_context(
    category="Spark Plugs",
    state=state,
    runtime=runtime
)

# Output:
{
    "category": "Spark Plugs",
    "relevant_insights": [
        {
            "content": "EV market growth 25% in 2024 reduces spark plug demand",
            "source": "IEA Report 2024",
            "relevance_score": 0.92
        },
        {
            "content": "Hybrid vehicles still require spark plugs, market stable",
            "source": "Automotive News",
            "relevance_score": 0.88
        }
    ]
}
```

Bước 2: analyze_category_with_api (Category-level)

```
# 1 lần cho toàn bộ category
category_insight = await analyze_category_with_api(
    category="Spark Plugs",
    category_context=category_context,
    state=state,
    runtime=runtime
)

# Output:
{
    "category": "Spark Plugs",
    "market_insight": "EV growth creates declining trend for spark plugs (-5% annually), but hybrid market provides stability. Premium iridium plugs maintain demand.",
    "key_findings": [
        "EV adoption reduces demand by 5% annually",
        "Hybrid vehicles stabilize market",
        "Premium segment (iridium) shows growth"
    ],
    "confidence_score": 0.85
}
```

Bước 3a: fuse_with_internal_data (Per-product)

```
# Cho MỖI product trong category
fused_data = await fuse_with_internal_data(
    product_code="VCH20",  # Bugi Iridium Tough
    market_insight=category_insight,  # REUSE từ bước 2
    state=state,
    runtime=runtime
)

# Output:
{
    "product_code": "VCH20",
    "product_name": "Bugi Ô Tô Iridium Tough VCH20",
    "category": "Spark Plugs",
    
    # Internal data từ mock
    "internal_data": {
        "historical_sales_full": [
            {"month": "2022-01", "quantity": 1200},
            {"month": "2022-02", "quantity": 1150},
            # ... 36 months
        ],
        "current_inventory": 850,
        "production_capacity": 5000,
        "quality_metrics": {"defect_rate": 0.02}
    },
    
    # External insight (SHARED category-level)
    "market_insight": {
        "summary": "EV growth creates declining trend...",
        "key_findings": ["EV adoption reduces demand..."],
        "confidence_score": 0.85
    }
}
```

Bước 3b: generate_forecast (Per-product)

```
# Cho MỖI product
forecast = await generate_forecast(
    product_code="VCH20",
    fused_data=fused_data,
    state=state,
    runtime=runtime
)

# Process:
# 1. Extract 36 months historical sales
historical_sales = fused_data["internal_data"]["historical_sales_full"]
#    [
#      {"month": "2022-01", "quantity": 1200},
#      ...
#      {"month": "2024-12", "quantity": 980}  # Declining trend
#    ]

# 2. Prophet forecasting
df = pd.DataFrame([
    {"ds": "2022-01-01", "y": 1200},
    {"ds": "2022-02-01", "y": 1150},
    # ... 36 rows
])

model = Prophet()
model.fit(df)

future = model.make_future_dataframe(periods=3, freq='MS')  # 3 months
forecast_result = model.predict(future)

# 3. Apply market adjustment từ category insight
market_signal = "declining"  # từ "EV growth creates declining trend"
adjustment_factor = 0.95  # -5% due to EV impact

base_forecast = forecast_result['yhat'].tail(3).sum()  # VD: 2800 units
adjusted_forecast = base_forecast * adjustment_factor  # 2660 units

# Output:
{
    "product_code": "VCH20",
    "forecast_units": 2660,  # Q1 2025 total
    "monthly_breakdown": [
        {"month": "2025-01", "forecast": 900},
        {"month": "2025-02", "forecast": 880},
        {"month": "2025-03", "forecast": 880}
    ],
    "confidence_interval": {
        "lower": 2261,  # 2660 * 0.85
        "upper": 3059   # 2660 * 1.15
    },
    "method": "Prophet + Market Adjustment",
    "market_factor_applied": 0.95,
    "timestamp": "2025-01-15T10:10:00"
}
```

## 🔄 Toàn bộ workflow cho 1 category:

```
process_category_batch(category="Spark Plugs", products=["VCH20", "PK16TT"])

Step 1: Category-level context (1 lần)
    ↓
    retrieve_category_context("Spark Plugs")
    → ChromaDB query: "Spark Plugs automotive market trends"
    → Top-5 insights về Spark Plugs market

Step 2: Category-level analysis (1 lần)
    ↓
    analyze_category_with_api(category_context)
    → xAI API call: Analyze Spark Plugs market
    → Output: "EV growth declining trend -5%"

Step 3: Per-product processing (loop 2 products)
    ↓
    For VCH20:
        ├─ fuse_with_internal_data(VCH20, category_insight)
        │   ├─ Get: 36 months sales data từ mock
        │   └─ Merge: Internal data + Category insight
        │
        └─ generate_forecast(VCH20, fused_data)
            ├─ Prophet model: Fit 36 months → Predict 3 months
            ├─ Apply market adjustment: -5% từ category insight
            └─ Output: Forecast Q1 2025
    
    For PK16TT:
        ├─ fuse_with_internal_data(PK16TT, category_insight) ← REUSE category_insight!
        └─ generate_forecast(PK16TT, fused_data)

Return: [forecast_VCH20, forecast_PK16TT]
```

## 💡 Key Points:
### Optimization nhờ Category Batching:
#### ✅ Bước 1-2 chỉ chạy 1 lần cho toàn bộ category (2 products SHARE)

- 1 ChromaDB query thay vì 2
- 1 xAI API call thay vì 2

#### ✅ Bước 3 chạy per-product (vì mỗi product có internal data khác nhau)

- Historical sales riêng
- Inventory level riêng
- Production capacity riêng