"""
Database interface for Log Feeding Service
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..models import LogEntry


class DatabaseInterface(ABC):
    """Abstract interface for database operations"""
    
    @abstractmethod
    def store_log(self, log_entry: LogEntry) -> bool:
        pass
    
    @abstractmethod
    def query_logs(self, filters: Dict[str, Any], limit: int = 100) -> List[LogEntry]:
        pass
    
    @abstractmethod
    def get_log_by_id(self, log_id: str) -> Optional[LogEntry]:
        pass
    
    @abstractmethod
    def delete_logs_before(self, timestamp: datetime) -> int:
        pass
    
    @abstractmethod
    def get_log_stats(self) -> Dict[str, Any]:
        pass