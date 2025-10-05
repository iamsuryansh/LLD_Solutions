"""
Scaling and sharding strategies for log management
"""

from abc import ABC, abstractmethod
from typing import List, Dict, TYPE_CHECKING
from datetime import datetime

from ..models import LogEntry, LogLevel
from ..storage import DatabaseInterface

if TYPE_CHECKING:
    from .log_feeding_service import LogFeedingService


class ScalingStrategy(ABC):
    """Abstract base for scaling strategies"""
    
    @abstractmethod
    def route_log(self, log_entry: LogEntry) -> DatabaseInterface:
        pass


class ServiceBasedSharding(ScalingStrategy):
    """Shard logs based on service name"""
    
    def __init__(self, shard_map: Dict[str, DatabaseInterface]):
        self.shard_map = shard_map
        self.default_shard = list(shard_map.values())[0] if shard_map else None
    
    def route_log(self, log_entry: LogEntry) -> DatabaseInterface:
        return self.shard_map.get(log_entry.service, self.default_shard)


class TimeBasedSharding(ScalingStrategy):
    """Shard logs based on timestamp (e.g., daily shards)"""
    
    def __init__(self, time_shards: Dict[str, DatabaseInterface]):
        self.time_shards = time_shards  # e.g., {"2024-01": db1, "2024-02": db2}
    
    def route_log(self, log_entry: LogEntry) -> DatabaseInterface:
        time_key = log_entry.timestamp.strftime("%Y-%m")
        return self.time_shards.get(time_key, list(self.time_shards.values())[0])


class LoadBalancer:
    """Distributes load across multiple service instances"""
    
    def __init__(self, services: List['LogFeedingService']):
        self.services = services
        self.current_index = 0
    
    def get_next_service(self) -> 'LogFeedingService':
        """Round-robin load balancing"""
        service = self.services[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.services)
        return service