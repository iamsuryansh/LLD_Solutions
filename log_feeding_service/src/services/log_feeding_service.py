"""
Core log feeding service implementation
"""

from typing import List, Optional
from datetime import datetime, timedelta

from ..models import LogEntry, LogLevel
from ..storage import DatabaseInterface, ReplicationStrategy


class LogFeedingService:
    """Main service for handling log ingestion and management"""
    
    def __init__(self, primary_db: DatabaseInterface, 
                 replication_strategy: Optional[ReplicationStrategy] = None,
                 replica_dbs: Optional[List[DatabaseInterface]] = None):
        self.primary_db = primary_db
        self.replication_strategy = replication_strategy
        self.replica_dbs = replica_dbs or []
        
    def ingest_log(self, level: LogLevel, message: str, service: str,
                  metadata: Optional[dict] = None) -> str:
        """Ingest a new log entry and return its unique ID"""
        log_entry = LogEntry(
            level=level,
            message=message, 
            service=service,
            metadata=metadata or {}
        )
        
        if self.replication_strategy and self.replica_dbs:
            success = self.replication_strategy.replicate(
                log_entry, self.primary_db, self.replica_dbs)
        else:
            success = self.primary_db.store_log(log_entry)
        
        if success:
            return log_entry.log_id
        else:
            raise RuntimeError("Failed to store log entry")
    
    def batch_ingest_logs(self, logs: List[dict]) -> List[str]:
        """Batch ingest multiple log entries"""
        log_ids = []
        for log_data in logs:
            try:
                log_id = self.ingest_log(
                    level=LogLevel(log_data['level']),
                    message=log_data['message'],
                    service=log_data['service'],
                    metadata=log_data.get('metadata')
                )
                log_ids.append(log_id)
            except Exception as e:
                print(f"Failed to ingest log: {e}")
                # In production, implement proper error handling
        return log_ids
    
    def get_logs_by_service(self, service: str, 
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> List[LogEntry]:
        """Get logs filtered by service and optional time range"""
        filters = {"service": service}
        if start_time:
            filters["start_time"] = start_time
        if end_time:
            filters["end_time"] = end_time
        return self.primary_db.query_logs(filters)
    
    def get_logs_by_level(self, level: LogLevel,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> List[LogEntry]:
        """Get logs filtered by log level and optional time range"""
        filters = {"level": level}
        if start_time:
            filters["start_time"] = start_time
        if end_time:
            filters["end_time"] = end_time
        return self.primary_db.query_logs(filters)
    
    def get_recent_logs(self, minutes: int = 60) -> List[LogEntry]:
        """Get logs from the last N minutes"""
        start_time = datetime.now() - timedelta(minutes=minutes)
        filters = {"start_time": start_time}
        return self.primary_db.query_logs(filters)
    
    def get_log_stats(self) -> dict:
        """Get basic statistics about stored logs"""
        return self.primary_db.get_log_stats()