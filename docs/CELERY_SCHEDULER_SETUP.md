# DENSO Celery Scheduler Setup Guide

## 📦 Component 3: Scheduler (Celery Beat)

Hướng dẫn setup Celery + Redis để chạy forecast jobs tự động mỗi 2 giờ.

---

## 🚀 Quick Start

### 1. Khởi động Redis Container

```powershell
# Start Redis (message broker)
docker-compose up -d redis

# Kiểm tra Redis đang chạy
docker ps | findstr redis

# Test Redis connection
docker exec -it denso_redis redis-cli ping
# Expected: PONG
```

**Kết quả mong đợi:**
```
CONTAINER ID   IMAGE            STATUS         PORTS                    NAMES
xyz789abc123   redis:7-alpine   Up 10 seconds  0.0.0.0:6379->6379/tcp   denso_redis
```

### 2. Install Celery Dependencies

```powershell
# Từ thư mục backend
cd backend
pip install -r requirements.txt

# Packages installed:
# - celery>=5.3.0
# - redis>=5.0.0
# - flower>=2.0.0 (monitoring UI)
```

### 3. Verify Configuration

```powershell
# Check .env file có REDIS_URL
cat .env

# Nên thấy:
# REDIS_URL=redis://localhost:6379/0
```

---

## 🏃 Running Celery Components

### Terminal 1: Celery Worker

```powershell
# Từ thư mục backend
cd backend

# Start worker
celery -A app.celery_app worker --loglevel=info --pool=solo

# Windows users: Use --pool=solo (gevent not supported on Windows)
```

**Kết quả mong đợi:**
```
 -------------- celery@DESKTOP-XXXXX v5.3.0
--- ***** -----
-- ******* ---- Windows-10-10.0.19045-SP0 2025-01-15 14:30:00
- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         denso_forecast:0x1a2b3c4d5e6
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 4 (solo)
-- ******* ---- .> task events: OFF
--- ***** -----
 -------------- [queues]
                .> default          exchange=default(direct) key=default
                .> forecast         exchange=forecast(direct) key=forecast
                .> reports          exchange=reports(direct) key=reports
                .> maintenance      exchange=maintenance(direct) key=maintenance

[tasks]
  . app.tasks.forecast_tasks.cleanup_old_alerts
  . app.tasks.forecast_tasks.generate_daily_summary
  . app.tasks.forecast_tasks.run_scheduled_forecast

[2025-01-15 14:30:00,123: INFO/MainProcess] Connected to redis://localhost:6379/0
[2025-01-15 14:30:00,456: INFO/MainProcess] mingle: searching for neighbors
[2025-01-15 14:30:01,789: INFO/MainProcess] mingle: all alone
[2025-01-15 14:30:02,012: INFO/MainProcess] celery@DESKTOP ready.
```

### Terminal 2: Celery Beat (Scheduler)

```powershell
# Open new terminal, cd to backend
cd backend

# Start beat scheduler
celery -A app.celery_app beat --loglevel=info
```

**Kết quả mong đợi:**
```
celery beat v5.3.0 is starting.
__    -    ... __   -        _
LocalTime -> 2025-01-15 14:30:00
Configuration ->
    . broker -> redis://localhost:6379/0
    . loader -> celery.loaders.app.AppLoader
    . scheduler -> celery.beat.PersistentScheduler
    . db -> celerybeat-schedule
    . logfile -> [stderr]@%INFO
    . maxinterval -> 5.00 minutes (300s)

[2025-01-15 14:30:00,123: INFO/MainProcess] beat: Starting...
[2025-01-15 14:30:00,456: INFO/MainProcess] Scheduler: Sending due task 
    run-forecast-every-2-hours (app.tasks.forecast_tasks.run_scheduled_forecast)
```

### Terminal 3: Flower (Monitoring UI) - Optional

```powershell
# Open new terminal
cd backend

# Start Flower web interface
celery -A app.celery_app flower --port=5555
```

**Access Flower Dashboard:**
- URL: http://localhost:5555
- Features:
  - Real-time task monitoring
  - Worker status
  - Task history
  - Task success/failure rates
  - Resource usage graphs

---

## 🧪 Testing Celery Tasks

### Test 1: Manual Task Trigger (via API)

```powershell
# Trigger forecast job manually
curl -X POST http://localhost:8000/api/jobs/forecast/trigger

# Response:
{
  "job_id": "abc123-def456-ghi789",
  "status": "pending",
  "message": "Forecast job triggered successfully"
}
```

### Test 2: Check Job Status

```powershell
# Get job status (replace with actual job_id from above)
$jobId = "abc123-def456-ghi789"
curl http://localhost:8000/api/jobs/forecast/$jobId

# Response:
{
  "job_id": "abc123-def456-ghi789",
  "status": "SUCCESS",
  "result": {
    "status": "completed",
    "alerts_generated": 2,
    "summary": {
      "high_severity": 1,
      "medium_severity": 1,
      "low_severity": 0
    }
  }
}
```

### Test 3: Verify Alerts Created

```powershell
# Check alerts created by scheduled job
curl "http://localhost:8000/api/alerts?source=scheduled_job"

# Should see 2 new alerts:
# 1. capacity_warning (high)
# 2. demand_spike (medium)
```

### Test 4: Check Celery Stats

```powershell
curl http://localhost:8000/api/jobs/stats

# Response:
{
  "workers": {
    "active": 1,
    "active_tasks": {}
  },
  "registered_tasks": [
    "app.tasks.forecast_tasks.run_scheduled_forecast",
    "app.tasks.forecast_tasks.generate_daily_summary",
    "app.tasks.forecast_tasks.cleanup_old_alerts"
  ]
}
```

### Test 5: Direct Celery Task Call (Python)

```python
# Test from Python shell
from app.celery_app import celery_app
from app.tasks.forecast_tasks import run_scheduled_forecast

# Trigger task
task = run_scheduled_forecast.delay()

# Get task ID
print(f"Task ID: {task.id}")

# Check status (wait a few seconds)
import time
time.sleep(5)

result = task.get(timeout=10)
print(f"Result: {result}")
```

---

## 📅 Scheduled Tasks Overview

### 1. Forecast Job (Every 2 Hours)

**Schedule:** `0 */2 * * *` (Every 2 hours at :00 minutes)

**Task:** `run_scheduled_forecast`

**What it does:**
- Runs LangGraph forecast pipeline (Phase 1: Mock)
- Generates alerts based on forecast results
- Stores alerts in PostgreSQL
- Returns execution summary

**Example executions:**
- 00:00, 02:00, 04:00, 06:00, 08:00, 10:00, 12:00, 14:00, 16:00, 18:00, 20:00, 22:00

### 2. Daily Summary (8:00 AM)

**Schedule:** `0 8 * * *` (Every day at 8:00 AM)

**Task:** `generate_daily_summary`

**What it does:**
- Aggregates alert statistics
- Generates daily report
- (Phase 2: Send email/Slack notification)

### 3. Weekly Cleanup (Sunday Midnight)

**Schedule:** `0 0 * * 0` (Every Sunday at 00:00)

**Task:** `cleanup_old_alerts`

**What it does:**
- Deletes alerts older than 90 days
- Frees up database storage
- Returns cleanup summary

---

## 🔍 Monitoring & Debugging

### Check Worker Logs

```powershell
# Worker logs show task execution
[2025-01-15 14:00:00,123: INFO/MainProcess] Task app.tasks.forecast_tasks.run_scheduled_forecast[abc-123] received
[2025-01-15 14:00:00,456: INFO/ForkPoolWorker-1] 🚀 [TASK] Starting scheduled forecast at 2025-01-15 14:00:00
[2025-01-15 14:00:02,789: INFO/ForkPoolWorker-1] 📊 [FORECAST] Running mock forecast pipeline...
[2025-01-15 14:00:05,012: INFO/ForkPoolWorker-1] 🔔 [ALERT] Created: capacity_warning - high
[2025-01-15 14:00:05,345: INFO/ForkPoolWorker-1] 🔔 [ALERT] Created: demand_spike - medium
[2025-01-15 14:00:05,678: INFO/ForkPoolWorker-1] ✅ [TASK] Forecast completed successfully
[2025-01-15 14:00:05,901: INFO/ForkPoolWorker-1] Task app.tasks.forecast_tasks.run_scheduled_forecast[abc-123] succeeded
```

### Check Beat Scheduler Logs

```powershell
# Beat logs show scheduled task triggers
[2025-01-15 14:00:00,000: INFO/MainProcess] Scheduler: Sending due task run-forecast-every-2-hours
[2025-01-15 16:00:00,000: INFO/MainProcess] Scheduler: Sending due task run-forecast-every-2-hours
```

### Redis Monitoring

```powershell
# Connect to Redis CLI
docker exec -it denso_redis redis-cli

# Check keys
127.0.0.1:6379> KEYS *

# Check queue length
127.0.0.1:6379> LLEN celery

# Monitor commands in real-time
127.0.0.1:6379> MONITOR
```

### Flower Dashboard Metrics

Navigate to http://localhost:5555 to see:
- ✅ Task success rate
- ⏱️ Task execution time
- 📊 Tasks per minute
- 🖥️ Worker CPU/Memory usage
- 📈 Queue lengths

---

## 🎯 API Endpoints Summary

| **Method** | **Endpoint** | **Purpose** |
|------------|-------------|-------------|
| POST | `/api/jobs/forecast/trigger` | Manually trigger forecast job |
| GET | `/api/jobs/forecast/{job_id}` | Get job status |
| GET | `/api/jobs/forecast/history` | Job execution history |
| POST | `/api/jobs/forecast/{job_id}/cancel` | Cancel running job |
| GET | `/api/jobs/stats` | Celery worker statistics |

---

## 📊 Celery Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Celery System                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Celery Beat (Scheduler)                        │
│     └─ Checks schedule every 5 seconds             │
│     └─ Pushes due tasks to Redis queue             │
│                                                     │
│  2. Redis (Message Broker)                         │
│     └─ Stores task queue (celery)                  │
│     └─ Stores task results                         │
│                                                     │
│  3. Celery Worker (Executor)                       │
│     └─ Picks tasks from Redis                      │
│     └─ Executes async Python functions             │
│     └─ Stores results back to Redis                │
│                                                     │
│  4. FastAPI (Job API)                              │
│     └─ Trigger tasks manually                      │
│     └─ Query task status                           │
│                                                     │
│  5. Flower (Monitoring)                            │
│     └─ Web UI for task monitoring                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Worker not picking up tasks

```powershell
# Check worker is running
# Terminal should show "celery@DESKTOP ready"

# Check Redis connection
docker exec -it denso_redis redis-cli ping

# Check task is in queue
docker exec -it denso_redis redis-cli LLEN celery
```

### Task execution fails

```powershell
# Check worker logs for errors
# Look for Python exceptions in terminal output

# Check database connection
# Verify DATABASE_URL in .env is correct
```

### Beat not triggering tasks

```powershell
# Verify beat is running (separate terminal)
# Check beat logs for "Sending due task" messages

# Verify schedule in celery_app.py
# Schedule uses UTC timezone
```

### Redis connection refused

```powershell
# Start Redis container
docker-compose up -d redis

# Check Redis port
netstat -an | findstr 6379

# Update REDIS_URL in .env if needed
```

---

## ✅ Component 3 Implementation Summary

**Đã hoàn thành:**

✅ **Redis Container** - Message broker cho Celery  
✅ **Celery App Configuration** - Beat schedule mỗi 2 giờ  
✅ **3 Scheduled Tasks:**
   - `run_scheduled_forecast` - Every 2 hours
   - `generate_daily_summary` - Daily at 8 AM
   - `cleanup_old_alerts` - Weekly on Sunday

✅ **Job Management API** - 5 endpoints cho trigger/monitor  
✅ **Flower Monitoring** - Web UI tại port 5555  
✅ **Async Task Support** - Proper asyncio integration  
✅ **Retry Logic** - Auto-retry on failure (max 3 times)  
✅ **Task Queues** - 4 queues (default, forecast, reports, maintenance)  

**Performance:**

- **Task execution time**: ~5 seconds (mock)
- **Retry delay**: 5 minutes
- **Task timeout**: 30 minutes hard limit
- **Result expiration**: 1 hour

**Phase 1 Status:** ✅ Scheduler hoàn tất với mock forecast  
**Phase 2 TODO:** Integrate real LangGraph pipeline  

**Ready for:** WebSocket real-time push (Component 4) 🚀
