"""
In-memory database implementation for Log Feeding Service
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from threading import Lock
from .database_interface import DatabaseInterface
from ..models import LogEntry, LogLevel


class InMemoryDatabase(DatabaseInterface):
    """In-memory implementation for demo purposes"""
    
    def __init__(self):
        self.logs: Dict[str, LogEntry] = {}
        self.index_by_service: Dict[str, List[str]] = {}
        self.index_by_level: Dict[LogLevel, List[str]] = {}
        self.lock = Lock()
    
    def store_log(self, log_entry: LogEntry) -> bool:
        with self.lock:
            self.logs[log_entry.log_id] = log_entry
            
            # Update service index
            if log_entry.service not in self.index_by_service:
                self.index_by_service[log_entry.service] = []
            self.index_by_service[log_entry.service].append(log_entry.log_id)
            
            # Update level index
            if log_entry.level not in self.index_by_level:
                self.index_by_level[log_entry.level] = []
            self.index_by_level[log_entry.level].append(log_entry.log_id)
            
            return True
    
    def query_logs(self, filters: Dict[str, Any], limit: int = 100) -> List[LogEntry]:
        with self.lock:
            matching_ids = set(self.logs.keys())
            
            # Apply service filter
            if "service" in filters:
                service_ids = set(self.index_by_service.get(filters["service"], []))
                matching_ids &= service_ids
            
            # Apply level filter
            if "level" in filters:
                level = LogLevel.from_string(filters["level"]) if isinstance(filters["level"], str) else filters["level"]
                level_ids = set(self.index_by_level.get(level, []))
                matching_ids &= level_ids
            
            # Get matching logs and apply additional filters
            matching_logs = []
            for log_id in matching_ids:
                log_entry = self.logs[log_id]
                
                # Apply timestamp filters
                if "start_time" in filters:
                    if log_entry.timestamp < filters["start_time"]:
                        continue
                
                if "end_time" in filters:
                    if log_entry.timestamp > filters["end_time"]:
                        continue
                
                # Apply correlation_id filter
                if "correlation_id" in filters:
                    if log_entry.correlation_id != filters["correlation_id"]:
                        continue
                
                matching_logs.append(log_entry)
            
            # Sort by timestamp (newest first) and limit
            matching_logs.sort(key=lambda x: x.timestamp, reverse=True)
            return matching_logs[:limit]
    
    def get_log_by_id(self, log_id: str) -> Optional[LogEntry]:
        return self.logs.get(log_id)
    
    def delete_logs_before(self, timestamp: datetime) -> int:
        with self.lock:
            ids_to_delete = []
            for log_id, log_entry in self.logs.items():
                if log_entry.timestamp < timestamp:
                    ids_to_delete.append(log_id)
            
            for log_id in ids_to_delete:
                del self.logs[log_id]
            
            return len(ids_to_delete)
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get basic statistics about stored logs"""
        with self.lock:
            services = set()
            levels = set()
            for log_entry in self.logs.values():
                services.add(log_entry.service)
                levels.add(log_entry.level)
            
            return {
                "total_logs": len(self.logs),
                "services": list(services),
                "levels": list(levels),
                "services_count": len(services),
                "levels_count": len(levels)
            }