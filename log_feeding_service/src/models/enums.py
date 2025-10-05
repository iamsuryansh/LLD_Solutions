"""
Enums for Log Feeding Service
"""

from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"
    
    @classmethod
    def from_string(cls, level: str):
        """Convert string to LogLevel enum"""
        try:
            return cls[level.upper()]
        except KeyError:
            raise ValueError(f"Invalid log level: {level}")