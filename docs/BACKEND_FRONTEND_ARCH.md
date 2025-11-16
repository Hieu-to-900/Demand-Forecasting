# Implementation Roadmap

```
Phase 1 (MVP - Week 1): Core Components
├─ REST API (polling)
├─ Alert Storage (database)
└─ Basic Frontend Polling

Phase 2 (Week 2-3): Scheduled Jobs
├─ Scheduler (Celery Beat)
└─ Background job execution

Phase 3 (Week 3-4): Real-time Features
├─ WebSocket Server
├─ Frontend WebSocket Client
└─ Message Queue (Redis)

Phase 4 (Week 4+): External Integrations
├─ Email Integration
└─ Slack Integration
```

## Component 1: Alert Storage (Database)

Mục đích:
Lưu trữ persistent tất cả alerts để:

- Query historical alerts
- Track read/unread status
- Filter by severity, type, date
- Analytics và reporting

Implementation Guide:

Option 1: PostgreSQL (Recommended cho production)

✅ ACID compliance (data integrity)
✅ Complex queries với JOIN
✅ Full-text search
✅ Mature ecosystem
📦 Libraries: asyncpg, SQLAlchemy

📊 API Summary
Method	Endpoint	Purpose
GET	/health	Health check
GET	/api/alerts	List alerts (filtered)
GET	/api/alerts/stats	Alert statistics
GET	/api/alerts/unread	Unread alerts
GET	/api/alerts/{id}	Get alert by ID
POST	/api/alerts	Create new alert
POST	/api/alerts/{id}/mark-read	Mark as read
POST	/api/alerts/{id}/dismiss	Dismiss alert
POST	/api/alerts/mark-all-read	Mark all as read
DELETE	/api/alerts/{id}	Delete alert

View all at http://localhost:8000/docs#/

## Component 2: REST API (Polling Fallback)

Mục đích:
Cho phép Frontend fetch alerts thông qua HTTP requests, fallback khi WebSocket không available.

Implementation Guide:
A. Endpoints Cần Có:
1. GET /api/alerts

Purpose: Fetch alerts với filtering
Query params:
since: ISO timestamp (chỉ lấy alerts sau thời điểm này)
severity: Filter by severity
unread_only: Boolean (chỉ unread)
product_code: Filter by affected product
limit: Number of results (default 50)
Response: List of alerts + metadata
2. GET /api/alerts/{alert_id}

Purpose: Get chi tiết 1 alert
Response: Full alert object
3. POST /api/alerts/{alert_id}/mark-read

Purpose: Mark alert as read
Body: {"user_id": "user123"}
Response: Success status
4. POST /api/alerts/{alert_id}/dismiss

Purpose: Dismiss alert (user không quan tâm)
Response: Success status
5. GET /api/alerts/stats

Purpose: Get alert statistics
Response:
```
{
  "total_unread": 5,
  "by_severity": {"high": 2, "medium": 3},
  "by_type": {"logistics_delay": 1, "capacity_warning": 4}
}
```

B. Response Format:
```
{
  "alerts": [
    {
      "id": "abc-123",
      "alert_type": "logistics_delay",
      "severity": "high",
      "message": "Port congestion at Yokohama - 48h delay",
      "affected_products": ["VCH20", "PK16TT"],
      "timestamp": "2025-01-15T02:10:00Z",
      "read": false
    }
  ],
  "total": 5,
  "unread_count": 5,
  "has_more": false,
  "next_cursor": null
}
```
C. API Design Principles:
Pagination:

Cursor-based pagination (tốt hơn offset cho real-time data)
Hoặc timestamp-based (since parameter)
Caching:

Cache alerts list trong 30 seconds (reduce DB load)
Invalidate cache khi có alert mới
Rate Limiting:

Limit 60 requests/minute per user (tránh spam polling)
Error Handling:

400: Invalid parameters
401: Unauthorized
404: Alert not found
500: Server error

D. Integration với Alert Storage:
```
Frontend Request
    ↓
FastAPI Endpoint
    ↓
Query Database (với indexes)
    ↓
Format Response
    ↓
Return JSON to Frontend
```

## Component 3: Scheduler (Celery Beat)
Mục đích:
Tự động chạy forecast pipeline mỗi 2 giờ, không cần user trigger.

Implementation Guide:
A. Tại sao dùng Celery?
Celery = Distributed Task Queue

✅ Chạy background tasks asynchronously
✅ Scheduled tasks (Celery Beat)
✅ Retry logic nếu task fails
✅ Monitoring và logging
✅ Scalable (nhiều workers)
Alternatives:

APScheduler: Đơn giản hơn, nhưng ít features
Cron jobs: Basic, nhưng khó manage
Kubernetes CronJobs: Tốt nếu đã dùng K8s

B. Components của Celery:

```
┌─────────────────────────────────────────────┐
│  Celery Architecture                        │
├─────────────────────────────────────────────┤
│                                             │
│  1. Celery Beat (Scheduler)                │
│     └─ Schedule tasks theo cron expression │
│                                             │
│  2. Message Broker (Redis/RabbitMQ)        │
│     └─ Queue tasks chờ execution           │
│                                             │
│  3. Celery Workers (Executors)             │
│     └─ Pick tasks from queue và execute    │
│                                             │
│  4. Result Backend (Redis/DB)              │
│     └─ Store task results                  │
│                                             │
└─────────────────────────────────────────────┘
```

C. Setup Steps:
Step 1: Install Dependencies

Celery package
Message broker (Redis recommended)
Result backend (Redis hoặc database)
Step 2: Create Celery App

File: celery_app.py
Configure broker URL (Redis connection)
Configure result backend
Step 3: Define Tasks

Task: run_scheduled_forecast()
Task decorator: @celery_app.task
Async wrapper cho LangGraph
Step 4: Configure Beat Schedule

Schedule definition: Chạy mỗi 2 giờ
Cron expression: 0 */2 * * *
Task name mapping
Step 5: Start Workers

Command: celery -A celery_app worker
Number of workers: 2-4 (depends on load)
Step 6: Start Beat Scheduler

Command: celery -A celery_app beat
Single instance (không scale beat)

D. Task Workflow:

```
[02:00:00] Celery Beat triggers task
    ↓
Task pushed to Redis queue
    ↓
Celery Worker picks up task
    ↓
Execute: run_scheduled_forecast()
    ├─ Call LangGraph: graph.ainvoke(...)
    ├─ Wait for completion (~15 minutes)
    └─ Store result in Result Backend
    ↓
Task completes
    ↓
Celery logs success
```

E. Monitoring & Debugging:
Flower (Celery monitoring tool):

Web UI để xem tasks
- Real-time task status
- Worker statistics
- Failed tasks inspection
Logging:
- Log task start/end
- Log errors với traceback
- Alert nếu task fails 3 times liên tiếp
Retry Logic:
- Auto retry nếu task fails
- Max retries: 3
- Exponential backoff: 1m, 5m, 15m
  
## Component 4: WebSocket Server (FastAPI)

Mục đích:
Real-time push alerts đến clients đang online, không cần polling.

Implementation Guide:
A. WebSocket vs HTTP:


## Scheduler (Celery Beat): Chạy forecast mỗi 2 giờ
## Alert Storage (MongoDB/PostgreSQL): Lưu trữ alerts
## Message Queue (Redis Pub/Sub): Real-time broadcast
## WebSocket Server (FastAPI): Push alerts to online users
## REST API: Polling fallback cho offline users
## Email/Slack Integration: External notifications
## Frontend WebSocket Client: Real-time listener
## Frontend Polling: Fallback mechanism
