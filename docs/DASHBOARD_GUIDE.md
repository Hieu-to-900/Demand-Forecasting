# DENSO Demand Forecasting Dashboard

## 🎯 Overview

A comprehensive 4-tier dashboard for AI-powered demand forecasting and risk intelligence, specifically designed for DENSO automotive parts in the Vietnamese market.

## 📊 Dashboard Architecture

The dashboard answers **3 critical business questions**:

### **Tier 1: What's happening? (Current State)**
- **Component**: `KPIOverview`
- **Purpose**: 6 key performance indicators at a glance
- **KPIs**:
  - 📈 Forecast Accuracy (94.2%)
  - 📊 Demand Change (+12.5%)
  - 🚨 Risk Signals (7 alerts)
  - 📦 Inventory Cover (28 days)
  - ⚠️ Stockout Risk (Medium/45)
  - 🏭 Production Load (87%)

### **Tier 2: What will happen? (Future Projection)**
- **Component**: `ForecastVisualization`
- **Features**:
  - 📈 **Time Series Chart**: 90-day forecast with confidence bounds
  - 📦 **Product Breakdown**: Individual product forecasts with trends
  - 🔥 **Heatmap**: Demand intensity by category and month
  - 📊 **Model Metrics**: MAPE (5.8%), RMSE (287), R² (0.94)

### **Tier 3: What's the risk landscape? (Intelligence)**
- **Component**: `RiskIntelligence`
- **Features**:
  - 📰 **News Feed**: 7 risk signals with severity scoring
  - 📅 **Timeline**: Risk event frequency over time
  - 🏷️ **Keywords Cloud**: Trending topics (港口, 鋼材, EV, 季風)
  - 📊 **Distribution**: Risk by category (Supply Chain 35%, Market 25%)

### **Tier 4: What should we do? (Actionable Recommendations)**
- **Component**: `ActionRecommendations`
- **Features**:
  - 🔴 **High Priority**: Secure shipping route ($450K impact), Increase capacity ($680K)
  - 🟡 **Medium Priority**: Promotional campaign (8-12% share), Hedge steel ($120K)
  - 🔵 **Low Priority**: Optimize inventory (5-8% service), Apply for incentives ($200K)
  - ✅ **Status Tracking**: Pending → In Progress → Completed

## 🏗️ Component Structure

```
frontend/src/
├── NewDashboard.jsx              # Main dashboard orchestrator
├── data/
│   └── mockData.js               # Comprehensive Vietnamese market mock data
└── components/
    └── NewDashboard/
        ├── Header.jsx            # Global filters & notifications
        ├── Header.css
        ├── KPIOverview.jsx       # Tier 1: 6 KPI cards
        ├── KPIOverview.css
        ├── ForecastVisualization.jsx  # Tier 2: Charts & forecasts
        ├── ForecastVisualization.css
        ├── RiskIntelligence.jsx  # Tier 3: News & risk monitoring
        ├── RiskIntelligence.css
        ├── ActionRecommendations.jsx  # Tier 4: Action cards
        ├── ActionRecommendations.css
        └── NewDashboard.css      # Main layout & animations
```

## 🎨 Design Features

### Visual Design
- **Color Coding**: 
  - 🔴 High Risk/Priority: `#ef4444`
  - 🟡 Medium: `#f59e0b`
  - 🔵 Low: `#3b82f6`
  - ✅ Positive: `#10b981`
- **Responsive Grid**: 4-col desktop → 2-col tablet → 1-col mobile
- **Animations**: Staggered fade-in (0.1s delay per tier)

### Interactive Elements
- **Time Range Filter**: 7d, 30d, 90d, 6m, YTD
- **Multi-Select**: Products (Spark Plugs, AC System, Filters, Sensors)
- **Region Filter**: Hanoi, HCMC, Da Nang, Hai Phong
- **Search Box**: Real-time query
- **Notifications**: Bell with badge + dropdown (7 unread)

## 📦 Mock Data Structure

### Products (5 DENSO Items)
```javascript
{
  id: "BUGI-IRIDIUM-VCH20",
  name: "Bugi Iridium VCH20",
  price: 450000,  // VND
  category: "Spark Plugs"
}
```

### KPI Format
```javascript
{
  id: "forecast_accuracy",
  title: "Độ chính xác dự báo",
  value: 94.2,
  change: 2.3,
  trend: "up",
  status: "excellent",
  icon: "📈"
}
```

### News Risk Format
```javascript
{
  id: "risk-001",
  title: "Cảng Hải Phòng tắc nghẽn - Delay 7 ngày",
  risk_score: 85,
  category: "supply_chain",
  impact: "negative",
  affected_products: ["AC-COMPRESSOR", "AC-CONDENSER"],
  tags: ["Logistics", "Supply Chain", "Vietnam"]
}
```

### Action Format
```javascript
{
  id: "action-001",
  title: "Đảm bảo tuyến vận chuyển dự phòng",
  priority: "high",
  severity: "critical",
  estimated_impact: "Tiết kiệm $450K/tháng",
  deadline: "2025-02-15",
  status: "pending",
  action_items: ["Liên hệ đối tác logistics", "Đàm phán giá vận chuyển"]
}
```

## 🚀 Running the Dashboard

### Development Mode
```bash
cd frontend
npm install
npm run dev
```

Access at: `http://localhost:5173`

### Toggle Between Dashboards
- **New Dashboard** (Default): Comprehensive 4-tier layout
- **Old Dashboard**: Legacy view (preserved for comparison)
- Toggle button: Top-right corner (📊 New / 🔧 Old)

## 🔗 Backend Integration (Phase 2)

### API Endpoints to Connect
```javascript
// Replace mockData with real API calls
import { api } from './services/api';

// KPIs
GET /api/kpis?timeRange=90d

// Forecast
GET /api/forecast?products=BUGI-IRIDIUM&horizon=90

// News Risks
GET /api/alerts?type=news&severity=high

// Actions
GET /api/actions?status=pending
POST /api/actions/{id}/update
```

## 📱 Responsive Breakpoints

- **Desktop**: 1200px+ (4-col grid, full features)
- **Tablet**: 768px - 1199px (2-col grid, compact)
- **Mobile**: <768px (1-col, stacked layout)

## 🎯 Key Metrics (Mock Data Performance)

- **Forecast Accuracy**: 94.2% (+2.3%)
- **Demand Uplift**: +12.5% vs last period
- **Risk Signals**: 7 active alerts (+3)
- **Inventory Cover**: 28 days
- **Production Load**: 87% capacity (+8%)

## 🇻🇳 Vietnamese Market Context

### Geographic Coverage
- **Hanoi**: 128 demand index, 32 days cover
- **HCMC**: 145 demand index, 28 days cover
- **Da Nang**: 98 demand index, 35 days cover
- **Hai Phong**: 87 demand index, 42 days cover

### Product Categories
1. **Spark Plugs** (2 products): Iridium, Platinum
2. **AC System** (3 products): Compressor, Evaporator, Condenser
3. **Filters** (4 products): Oil, Air, Cabin, Fuel
4. **Sensors** (3 products): O2, MAP, Knock

## 🔧 Customization

### Adding New KPI
```javascript
// In mockData.js
export const mockData = {
  kpis: [
    ...mockData.kpis,
    {
      id: "new_kpi",
      title: "New Metric",
      value: 123,
      change: 5.2,
      trend: "up",
      status: "good",
      icon: "📊"
    }
  ]
};
```

### Adding New Action
```javascript
const newAction = {
  id: `action-${Date.now()}`,
  title: "New Recommendation",
  priority: "high",
  severity: "warning",
  estimated_impact: "$100K saving",
  deadline: "2025-03-01",
  status: "pending",
  action_items: ["Step 1", "Step 2"]
};
```

## 📚 Dependencies

- **React 18**: UI framework
- **Recharts**: Chart library
- **date-fns**: Date formatting
- **axios**: HTTP client (for backend integration)

## 🎓 Design Philosophy

1. **Information Hierarchy**: Most critical data at top (KPIs)
2. **Progressive Disclosure**: Details on demand (click to expand)
3. **Actionable Intelligence**: Every insight → recommended action
4. **Vietnamese Context**: Local market data, VND pricing, Vietnamese labels
5. **Real-time Ready**: Mock data → API integration path clear

## 🚧 Roadmap (Phase 2)

- [ ] Connect to backend REST APIs
- [ ] WebSocket for real-time alerts
- [ ] Export to PDF/Excel
- [ ] User preferences persistence
- [ ] Mobile app (React Native)
- [ ] Multi-language support (EN/VI toggle)

---

**Built for**: DENSO HackAthon 2025  
**Stack**: React 18 + Vite + Recharts  
**Market**: Vietnamese Automotive Aftermarket  
**Status**: ✅ Frontend Complete | 🚧 Backend Integration Pending
