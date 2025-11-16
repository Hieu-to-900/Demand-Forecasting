"""Tasks package for Celery background jobs."""

from app.tasks.forecast_tasks import (
    cleanup_old_alerts,
    generate_daily_summary,
    run_scheduled_forecast,
)

__all__ = [
    "run_scheduled_forecast",
    "generate_daily_summary",
    "cleanup_old_alerts",
]
