"""Celery tasks for demand forecasting."""

import asyncio
from datetime import datetime
from typing import Any, Dict

from celery import Task

from app.celery_app import celery_app
from app.database.connection import Database
from app.models.alert import AlertCreate
from app.repositories.alert_repository import AlertRepository


class AsyncTask(Task):
    """Base task with async support."""
    
    _db: Database = None
    
    @property
    def db(self) -> Database:
        """Get database connection."""
        if self._db is None:
            self._db = Database()
            # Initialize connection pool
            asyncio.run(self._db.connect())
        return self._db


@celery_app.task(
    bind=True,
    base=AsyncTask,
    name="app.tasks.forecast_tasks.run_scheduled_forecast",
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def run_scheduled_forecast(self) -> Dict[str, Any]:
    """Run demand forecast pipeline every 2 hours.
    
    This task:
    1. Triggers LangGraph forecast pipeline
    2. Generates alerts based on forecast results
    3. Stores alerts in database
    4. Returns execution summary
    """
    try:
        print(f"🚀 [TASK] Starting scheduled forecast at {datetime.utcnow()}")
        
        # Run async forecast function
        result = asyncio.run(_run_forecast_async(self.db))
        
        print(f"✅ [TASK] Forecast completed successfully")
        return result
        
    except Exception as exc:
        print(f"❌ [TASK] Forecast failed: {str(exc)}")
        # Retry on failure
        raise self.retry(exc=exc)


async def _run_forecast_async(db: Database) -> Dict[str, Any]:
    """Async implementation of forecast pipeline.
    
    Phase 1: Mock implementation
    Phase 2: Real LangGraph integration
    """
    # TODO Phase 2: Integrate with LangGraph
    # from src.agent.graph import graph
    # result = await graph.ainvoke({
    #     "product_codes": await _get_all_product_codes(),
    #     "chromadb_collection": "external_market_data"
    # })
    
    # Phase 1: Mock forecast execution
    print("📊 [FORECAST] Running mock forecast pipeline...")
    await asyncio.sleep(2)  # Simulate processing
    
    # Mock forecast results
    mock_alerts = [
        {
            "alert_type": "capacity_warning",
            "severity": "high",
            "message": "Production capacity projected to reach 95% utilization in Q1 2025",
            "affected_products": ["BUGI-IRIDIUM-VCH20", "AC-COMPRESSOR-6SEU14C"],
            "affected_categories": ["Spark_Plugs", "AC_System"],
            "impact_description": "Forecast demand exceeds current capacity by 2,500 units",
            "action_required": "Schedule additional shifts or contract third-party manufacturers",
            "source": "scheduled_job",
            "metadata": {
                "forecast_period": "Q1_2025",
                "utilization_rate": 0.95,
                "shortfall_units": 2500,
                "execution_time": datetime.utcnow().isoformat(),
            },
            "priority_score": 90,
        },
        {
            "alert_type": "demand_spike",
            "severity": "medium",
            "message": "15% demand increase detected for Spark Plugs category",
            "affected_products": ["BUGI-IRIDIUM-VCH20", "BUGI-PLATIN-PK16TT"],
            "affected_categories": ["Spark_Plugs"],
            "impact_description": "Market analysis indicates increased vehicle maintenance activity",
            "action_required": "Increase raw material orders and adjust production schedule",
            "source": "scheduled_job",
            "metadata": {
                "demand_increase": 0.15,
                "market_factor": "seasonal",
                "confidence": 0.87,
            },
            "priority_score": 70,
        },
    ]
    
    # Store alerts in database
    repo = AlertRepository(db)
    created_alerts = []
    
    for alert_data in mock_alerts:
        alert = AlertCreate(**alert_data)
        created_alert = await repo.create_alert(alert)
        created_alerts.append(created_alert)
        print(f"🔔 [ALERT] Created: {created_alert.alert_type} - {created_alert.severity}")
    
    return {
        "status": "completed",
        "execution_time": datetime.utcnow().isoformat(),
        "alerts_generated": len(created_alerts),
        "alert_ids": [str(alert.id) for alert in created_alerts],
        "summary": {
            "high_severity": sum(1 for a in created_alerts if a.severity == "high"),
            "medium_severity": sum(1 for a in created_alerts if a.severity == "medium"),
            "low_severity": sum(1 for a in created_alerts if a.severity == "low"),
        },
    }


@celery_app.task(
    bind=True,
    base=AsyncTask,
    name="app.tasks.forecast_tasks.generate_daily_summary",
)
def generate_daily_summary(self) -> Dict[str, Any]:
    """Generate daily forecast summary report.
    
    Runs every day at 8 AM to summarize alerts and forecasts.
    """
    try:
        print(f"📊 [TASK] Generating daily summary at {datetime.utcnow()}")
        
        result = asyncio.run(_generate_summary_async(self.db))
        
        print(f"✅ [TASK] Daily summary completed")
        return result
        
    except Exception as exc:
        print(f"❌ [TASK] Summary generation failed: {str(exc)}")
        raise self.retry(exc=exc)


async def _generate_summary_async(db: Database) -> Dict[str, Any]:
    """Generate summary report."""
    repo = AlertRepository(db)
    stats = await repo.get_alert_stats()
    
    summary = {
        "date": datetime.utcnow().date().isoformat(),
        "total_alerts": stats.total_alerts,
        "unread_alerts": stats.unread_count,
        "alerts_by_severity": stats.by_severity,
        "alerts_by_type": stats.by_type,
        "latest_alert": stats.latest_alert.isoformat() if stats.latest_alert else None,
    }
    
    print(f"📈 [SUMMARY] Total alerts: {stats.total_alerts}, Unread: {stats.unread_count}")
    
    # TODO: Send summary email/Slack notification
    # await send_email_summary(summary)
    # await send_slack_summary(summary)
    
    return summary


@celery_app.task(
    bind=True,
    base=AsyncTask,
    name="app.tasks.forecast_tasks.cleanup_old_alerts",
)
def cleanup_old_alerts(self, days: int = 90) -> Dict[str, Any]:
    """Cleanup alerts older than specified days.
    
    Runs weekly on Sunday at midnight.
    
    Args:
        days: Delete alerts older than this many days (default: 90)
    """
    try:
        print(f"🧹 [TASK] Starting cleanup of alerts older than {days} days")
        
        result = asyncio.run(_cleanup_alerts_async(self.db, days))
        
        print(f"✅ [TASK] Cleanup completed: {result['deleted_count']} alerts deleted")
        return result
        
    except Exception as exc:
        print(f"❌ [TASK] Cleanup failed: {str(exc)}")
        raise self.retry(exc=exc)


async def _cleanup_alerts_async(db: Database, days: int) -> Dict[str, Any]:
    """Cleanup old alerts."""
    repo = AlertRepository(db)
    deleted_count = await repo.delete_old_alerts(days)
    
    return {
        "deleted_count": deleted_count,
        "threshold_days": days,
        "execution_time": datetime.utcnow().isoformat(),
    }


# Helper function for Phase 2 integration
async def _get_all_product_codes() -> list[str]:
    """Get all product codes from category mock data.
    
    Phase 2: Replace with real database query.
    """
    # TODO: Import from category_products_mock
    return [
        "BUGI-IRIDIUM-VCH20",
        "BUGI-PLATIN-PK16TT",
        "AC-COMPRESSOR-6SEU14C",
        "AC-EVAPORATOR-CORE",
        "AC-CONDENSER-CORE",
    ]
