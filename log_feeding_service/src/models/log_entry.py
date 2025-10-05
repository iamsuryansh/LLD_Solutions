"""
Log Entry model for Log Feeding Service
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any
import uuid
from .enums import LogLevel


@dataclass
class LogEntry:
    """Core log entry model"""
    level: LogLevel
    message: str
    service: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "log_id": self.log_id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "service": self.service,
            "message": self.message,
            "metadata": self.metadata,
            "source_ip": self.source_ip,
            "correlation_id": self.correlation_id
        }