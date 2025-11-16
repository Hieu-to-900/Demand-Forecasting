"""Alert repository for database operations."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

import asyncpg

from app.database.connection import Database
from app.models.alert import Alert, AlertCreate, AlertStats, AlertUpdate


class AlertRepository:
    """Repository for alert database operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create_alert(self, alert: AlertCreate) -> Alert:
        """Create a new alert."""
        query = """
            INSERT INTO alerts (
                alert_type, severity, message, affected_products, affected_categories,
                impact_description, action_required, source, metadata, priority_score
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING *
        """
        
        row = await self.db.fetch_one(
            query,
            alert.alert_type,
            alert.severity,
            alert.message,
            alert.affected_products,
            alert.affected_categories,
            alert.impact_description,
            alert.action_required,
            alert.source,
            alert.metadata,
            alert.priority_score,
        )
        
        return self._row_to_alert(row)
    
    async def get_alert(self, alert_id: UUID) -> Optional[Alert]:
        """Get alert by ID."""
        query = "SELECT * FROM alerts WHERE id = $1"
        row = await self.db.fetch_one(query, alert_id)
        
        if row:
            return self._row_to_alert(row)
        return None
    
    async def get_alerts(
        self,
        since: Optional[datetime] = None,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        unread_only: bool = False,
        product_code: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Alert]:
        """Get alerts with filtering."""
        conditions = ["dismissed = FALSE"]
        params = []
        param_count = 1
        
        if since:
            conditions.append(f"created_at > ${param_count}")
            params.append(since)
            param_count += 1
        
        if severity:
            conditions.append(f"severity = ${param_count}")
            params.append(severity)
            param_count += 1
        
        if alert_type:
            conditions.append(f"alert_type = ${param_count}")
            params.append(alert_type)
            param_count += 1
        
        if unread_only:
            conditions.append("read = FALSE")
        
        if product_code:
            conditions.append(f"${param_count} = ANY(affected_products)")
            params.append(product_code)
            param_count += 1
        
        where_clause = " AND ".join(conditions)
        params.extend([limit, offset])
        
        query = f"""
            SELECT * FROM alerts
            WHERE {where_clause}
            ORDER BY priority_score DESC, created_at DESC
            LIMIT ${param_count} OFFSET ${param_count + 1}
        """
        
        rows = await self.db.fetch_all(query, *params)
        return [self._row_to_alert(row) for row in rows]
    
    async def update_alert(self, alert_id: UUID, update: AlertUpdate) -> Optional[Alert]:
        """Update alert."""
        updates = []
        params = []
        param_count = 1
        
        if update.read is not None:
            updates.append(f"read = ${param_count}")
            params.append(update.read)
            param_count += 1
            
            if update.read:
                updates.append(f"read_at = ${param_count}")
                params.append(datetime.utcnow())
                param_count += 1
        
        if update.read_by is not None:
            updates.append(f"read_by = ${param_count}")
            params.append(update.read_by)
            param_count += 1
        
        if update.dismissed is not None:
            updates.append(f"dismissed = ${param_count}")
            params.append(update.dismissed)
            param_count += 1
            
            if update.dismissed:
                updates.append(f"dismissed_at = ${param_count}")
                params.append(datetime.utcnow())
                param_count += 1
        
        if not updates:
            return await self.get_alert(alert_id)
        
        set_clause = ", ".join(updates)
        params.append(alert_id)
        
        query = f"""
            UPDATE alerts
            SET {set_clause}
            WHERE id = ${param_count}
            RETURNING *
        """
        
        row = await self.db.fetch_one(query, *params)
        
        if row:
            return self._row_to_alert(row)
        return None
    
    async def get_alert_stats(self) -> AlertStats:
        """Get alert statistics."""
        # Total and unread counts
        count_query = """
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE read = FALSE) as unread
            FROM alerts
            WHERE dismissed = FALSE
        """
        count_row = await self.db.fetch_one(count_query)
        
        # By severity
        severity_query = """
            SELECT severity, COUNT(*) as count
            FROM alerts
            WHERE dismissed = FALSE
            GROUP BY severity
        """
        severity_rows = await self.db.fetch_all(severity_query)
        by_severity = {row['severity']: row['count'] for row in severity_rows}
        
        # By type
        type_query = """
            SELECT alert_type, COUNT(*) as count
            FROM alerts
            WHERE dismissed = FALSE
            GROUP BY alert_type
        """
        type_rows = await self.db.fetch_all(type_query)
        by_type = {row['alert_type']: row['count'] for row in type_rows}
        
        # Latest alert
        latest_query = """
            SELECT MAX(created_at) as latest
            FROM alerts
            WHERE dismissed = FALSE
        """
        latest_row = await self.db.fetch_one(latest_query)
        
        return AlertStats(
            total_alerts=count_row['total'],
            unread_count=count_row['unread'],
            by_severity=by_severity,
            by_type=by_type,
            latest_alert=latest_row['latest'],
        )
    
    async def get_unread_summary(self) -> List[Dict]:
        """Get unread alerts summary."""
        query = "SELECT * FROM unread_alerts_summary"
        rows = await self.db.fetch_all(query)
        return [dict(row) for row in rows]
    
    async def delete_old_alerts(self, days: int = 90) -> int:
        """Delete alerts older than specified days."""
        query = """
            DELETE FROM alerts
            WHERE created_at < NOW() - INTERVAL '%s days'
            RETURNING id
        """
        result = await self.db.execute(query, days)
        # Extract count from result string like "DELETE 5"
        return int(result.split()[-1]) if result else 0
    
    @staticmethod
    def _row_to_alert(row: asyncpg.Record) -> Alert:
        """Convert database row to Alert model."""
        return Alert(
            id=row['id'],
            alert_type=row['alert_type'],
            severity=row['severity'],
            message=row['message'],
            affected_products=row['affected_products'] or [],
            affected_categories=row['affected_categories'] or [],
            impact_description=row['impact_description'],
            action_required=row['action_required'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            read=row['read'],
            read_at=row['read_at'],
            read_by=row['read_by'],
            dismissed=row['dismissed'],
            dismissed_at=row['dismissed_at'],
            source=row['source'],
            metadata=row['metadata'] or {},
            priority_score=row['priority_score'],
        )
