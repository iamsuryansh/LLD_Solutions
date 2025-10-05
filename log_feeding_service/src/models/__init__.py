"""
Models package for Log Feeding Service
"""

from .enums import LogLevel
from .log_entry import LogEntry

__all__ = ['LogLevel', 'LogEntry']