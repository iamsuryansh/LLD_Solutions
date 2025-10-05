"""
Log filtering functionality
"""

from abc import ABC, abstractmethod
from typing import List, Set, Optional
from datetime import datetime

from ..models import LogEntry, LogLevel


class LogFilter(ABC):
    """Abstract base for log filters"""
    
    @abstractmethod
    def apply(self, logs: List[LogEntry]) -> List[LogEntry]:
        pass


class LevelFilter(LogFilter):
    """Filter logs by log level"""
    
    def __init__(self, levels: Set[LogLevel]):
        self.levels = levels
    
    def apply(self, logs: List[LogEntry]) -> List[LogEntry]:
        return [log for log in logs if log.level in self.levels]


class ServiceFilter(LogFilter):
    """Filter logs by service name"""
    
    def __init__(self, services: Set[str]):
        self.services = services
    
    def apply(self, logs: List[LogEntry]) -> List[LogEntry]:
        return [log for log in logs if log.service in self.services]


class TimeRangeFilter(LogFilter):
    """Filter logs by time range"""
    
    def __init__(self, start_time: Optional[datetime] = None, 
                 end_time: Optional[datetime] = None):
        self.start_time = start_time
        self.end_time = end_time
    
    def apply(self, logs: List[LogEntry]) -> List[LogEntry]:
        filtered_logs = logs
        
        if self.start_time:
            filtered_logs = [log for log in filtered_logs 
                           if log.timestamp >= self.start_time]
        
        if self.end_time:
            filtered_logs = [log for log in filtered_logs 
                           if log.timestamp <= self.end_time]
        
        return filtered_logs


class KeywordFilter(LogFilter):
    """Filter logs by keywords in message"""
    
    def __init__(self, keywords: Set[str], case_sensitive: bool = False):
        self.keywords = keywords if case_sensitive else {kw.lower() for kw in keywords}
        self.case_sensitive = case_sensitive
    
    def apply(self, logs: List[LogEntry]) -> List[LogEntry]:
        filtered_logs = []
        for log in logs:
            message = log.message if self.case_sensitive else log.message.lower()
            if any(keyword in message for keyword in self.keywords):
                filtered_logs.append(log)
        return filtered_logs


class CompositeFilter(LogFilter):
    """Combines multiple filters using AND logic"""
    
    def __init__(self, filters: List[LogFilter]):
        self.filters = filters
    
    def apply(self, logs: List[LogEntry]) -> List[LogEntry]:
        filtered_logs = logs
        for filter_instance in self.filters:
            filtered_logs = filter_instance.apply(filtered_logs)
        return filtered_logs