"""
Log Feeding Service - Low Level Design Implementation

A distributed log collection and management system that handles log ingestion,
storage, filtering, and querying with proper scaling and replication strategies.

Author: Interview Practice
Time: ~60 minutes
Key Concepts: Observer Pattern, Strategy Pattern, Database Design, REST APIs, Scaling
"""

import uuid
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import Lock
import hashlib


# ================================
# Core Models and Enums
# ================================

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


@dataclass
class LogEntry:
    """Core log entry model"""
    id: str
    timestamp: datetime
    level: LogLevel
    service_name: str
    message: str
    metadata: Dict[str, Any]
    source_ip: str = ""
    correlation_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "service_name": self.service_name,
            "message": self.message,
            "metadata": self.metadata,
            "source_ip": self.source_ip,
            "correlation_id": self.correlation_id
        }


# ================================
# Storage Layer Interfaces
# ================================

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


class InMemoryDatabase(DatabaseInterface):
    """In-memory implementation for demo purposes"""
    
    def __init__(self):
        self.logs: Dict[str, LogEntry] = {}
        self.index_by_service: Dict[str, List[str]] = {}
        self.index_by_level: Dict[LogLevel, List[str]] = {}
        self.lock = Lock()
    
    def store_log(self, log_entry: LogEntry) -> bool:
        with self.lock:
            self.logs[log_entry.id] = log_entry
            
            # Update service index
            if log_entry.service_name not in self.index_by_service:
                self.index_by_service[log_entry.service_name] = []
            self.index_by_service[log_entry.service_name].append(log_entry.id)
            
            # Update level index
            if log_entry.level not in self.index_by_level:
                self.index_by_level[log_entry.level] = []
            self.index_by_level[log_entry.level].append(log_entry.id)
            
            return True
    
    def query_logs(self, filters: Dict[str, Any], limit: int = 100) -> List[LogEntry]:
        with self.lock:
            matching_ids = set(self.logs.keys())
            
            # Apply service filter
            if "service_name" in filters:
                service_ids = set(self.index_by_service.get(filters["service_name"], []))
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


# ================================
# Replication Strategy
# ================================

class ReplicationStrategy(ABC):
    """Abstract base for replication strategies"""
    
    @abstractmethod
    def replicate(self, log_entry: LogEntry, primary_db: DatabaseInterface, 
                 replica_dbs: List[DatabaseInterface]) -> bool:
        pass


class MasterSlaveReplication(ReplicationStrategy):
    """Master-slave replication strategy"""
    
    def replicate(self, log_entry: LogEntry, primary_db: DatabaseInterface, 
                 replica_dbs: List[DatabaseInterface]) -> bool:
        # Store in primary first
        if not primary_db.store_log(log_entry):
            return False
        
        # Asynchronously replicate to slaves (simplified synchronous for demo)
        for replica in replica_dbs:
            try:
                replica.store_log(log_entry)
            except Exception as e:
                print(f"Replication failed to replica: {e}")
                # In production, implement retry logic and error handling
        
        return True


# ================================
# Filter System
# ================================

class LogFilter(ABC):
    """Abstract base for log filters"""
    
    @abstractmethod
    def should_process(self, log_entry: LogEntry) -> bool:
        pass


class LevelFilter(LogFilter):
    """Filter logs by minimum level"""
    
    def __init__(self, min_level: LogLevel):
        self.min_level = min_level
        self.level_hierarchy = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARN: 2,
            LogLevel.ERROR: 3,
            LogLevel.FATAL: 4
        }
    
    def should_process(self, log_entry: LogEntry) -> bool:
        return self.level_hierarchy[log_entry.level] >= self.level_hierarchy[self.min_level]


class ServiceFilter(LogFilter):
    """Filter logs by allowed services"""
    
    def __init__(self, allowed_services: List[str]):
        self.allowed_services = set(allowed_services)
    
    def should_process(self, log_entry: LogEntry) -> bool:
        return log_entry.service_name in self.allowed_services


class CompositeFilter(LogFilter):
    """Combines multiple filters with AND logic"""
    
    def __init__(self, filters: List[LogFilter]):
        self.filters = filters
    
    def should_process(self, log_entry: LogEntry) -> bool:
        return all(f.should_process(log_entry) for f in self.filters)


# ================================
# ID Generation Strategy
# ================================

class IDGenerator(ABC):
    """Abstract ID generator"""
    
    @abstractmethod
    def generate_id(self, log_entry: LogEntry) -> str:
        pass


class UUIDGenerator(IDGenerator):
    """UUID-based ID generation"""
    
    def generate_id(self, log_entry: LogEntry) -> str:
        return str(uuid.uuid4())


class SnowflakeIDGenerator(IDGenerator):
    """Simplified Snowflake-like ID generation (demo version)"""
    
    def __init__(self, machine_id: int = 1):
        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = 0
    
    def generate_id(self, log_entry: LogEntry) -> str:
        timestamp = int(time.time() * 1000)  # milliseconds
        
        if timestamp == self.last_timestamp:
            self.sequence += 1
        else:
            self.sequence = 0
            self.last_timestamp = timestamp
        
        # Simple concatenation for demo (real Snowflake uses bit shifting)
        return f"{timestamp}-{self.machine_id}-{self.sequence}"


# ================================
# Core Log Feeding Service
# ================================

class LogFeedingService:
    """Main service for log collection and management"""
    
    def __init__(self, 
                 primary_db: DatabaseInterface,
                 replica_dbs: List[DatabaseInterface] = None,
                 replication_strategy: ReplicationStrategy = None,
                 id_generator: IDGenerator = None,
                 filters: List[LogFilter] = None):
        
        self.primary_db = primary_db
        self.replica_dbs = replica_dbs or []
        self.replication_strategy = replication_strategy or MasterSlaveReplication()
        self.id_generator = id_generator or UUIDGenerator()
        self.filters = filters or []
        
        # Metrics and monitoring
        self.metrics = {
            "logs_received": 0,
            "logs_processed": 0,
            "logs_filtered": 0,
            "errors": 0
        }
    
    def ingest_log(self, level: str, service_name: str, message: str, 
                  metadata: Dict[str, Any] = None, correlation_id: str = "",
                  source_ip: str = "") -> str:
        """Ingest a new log entry"""
        
        self.metrics["logs_received"] += 1
        
        try:
            # Create log entry
            log_entry = LogEntry(
                id="",  # Will be set by ID generator
                timestamp=datetime.now(),
                level=LogLevel.from_string(level),
                service_name=service_name,
                message=message,
                metadata=metadata or {},
                source_ip=source_ip,
                correlation_id=correlation_id
            )
            
            # Generate unique ID
            log_entry.id = self.id_generator.generate_id(log_entry)
            
            # Apply filters
            for log_filter in self.filters:
                if not log_filter.should_process(log_entry):
                    self.metrics["logs_filtered"] += 1
                    return log_entry.id  # Still return ID even if filtered
            
            # Store with replication
            success = self.replication_strategy.replicate(
                log_entry, self.primary_db, self.replica_dbs
            )
            
            if success:
                self.metrics["logs_processed"] += 1
            else:
                self.metrics["errors"] += 1
                raise Exception("Failed to store log entry")
            
            return log_entry.id
            
        except Exception as e:
            self.metrics["errors"] += 1
            raise e
    
    def query_logs(self, service_name: str = None, level: str = None,
                  start_time: datetime = None, end_time: datetime = None,
                  correlation_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Query logs with various filters"""
        
        filters = {}
        if service_name:
            filters["service_name"] = service_name
        if level:
            filters["level"] = level
        if start_time:
            filters["start_time"] = start_time
        if end_time:
            filters["end_time"] = end_time
        if correlation_id:
            filters["correlation_id"] = correlation_id
        
        logs = self.primary_db.query_logs(filters, limit)
        return [log.to_dict() for log in logs]
    
    def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific log by ID"""
        log_entry = self.primary_db.get_log_by_id(log_id)
        return log_entry.to_dict() if log_entry else None
    
    def get_metrics(self) -> Dict[str, int]:
        """Get service metrics"""
        return self.metrics.copy()
    
    def cleanup_old_logs(self, before_timestamp: datetime) -> int:
        """Clean up old logs (retention policy)"""
        return self.primary_db.delete_logs_before(before_timestamp)


# ================================
# REST API Layer (Simplified)
# ================================

class LogFeedingAPI:
    """REST API endpoints for the log feeding service"""
    
    def __init__(self, log_service: LogFeedingService):
        self.log_service = log_service
    
    def post_log(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/v1/logs - Ingest a new log"""
        try:
            # Validate required fields
            required_fields = ["level", "service_name", "message"]
            for field in required_fields:
                if field not in request_data:
                    return {
                        "error": f"Missing required field: {field}",
                        "status": 400
                    }
            
            log_id = self.log_service.ingest_log(
                level=request_data["level"],
                service_name=request_data["service_name"],
                message=request_data["message"],
                metadata=request_data.get("metadata", {}),
                correlation_id=request_data.get("correlation_id", ""),
                source_ip=request_data.get("source_ip", "")
            )
            
            return {
                "log_id": log_id,
                "status": 201,
                "message": "Log ingested successfully"
            }
            
        except ValueError as e:
            return {"error": str(e), "status": 400}
        except Exception as e:
            return {"error": "Internal server error", "status": 500}
    
    def get_logs(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """GET /api/v1/logs - Query logs"""
        try:
            # Parse query parameters
            start_time = None
            end_time = None
            
            if "start_time" in query_params:
                start_time = datetime.fromisoformat(query_params["start_time"])
            if "end_time" in query_params:
                end_time = datetime.fromisoformat(query_params["end_time"])
            
            logs = self.log_service.query_logs(
                service_name=query_params.get("service_name"),
                level=query_params.get("level"),
                start_time=start_time,
                end_time=end_time,
                correlation_id=query_params.get("correlation_id"),
                limit=int(query_params.get("limit", 100))
            )
            
            return {
                "logs": logs,
                "count": len(logs),
                "status": 200
            }
            
        except ValueError as e:
            return {"error": f"Invalid parameter: {e}", "status": 400}
        except Exception as e:
            return {"error": "Internal server error", "status": 500}
    
    def get_log_by_id(self, log_id: str) -> Dict[str, Any]:
        """GET /api/v1/logs/{id} - Get specific log"""
        try:
            log_entry = self.log_service.get_log_by_id(log_id)
            if log_entry:
                return {"log": log_entry, "status": 200}
            else:
                return {"error": "Log not found", "status": 404}
                
        except Exception as e:
            return {"error": "Internal server error", "status": 500}
    
    def get_metrics(self) -> Dict[str, Any]:
        """GET /api/v1/metrics - Get service metrics"""
        try:
            metrics = self.log_service.get_metrics()
            return {"metrics": metrics, "status": 200}
        except Exception as e:
            return {"error": "Internal server error", "status": 500}


# ================================
# Demo and Testing
# ================================

def demo_log_feeding_service():
    """Demonstrate the log feeding service functionality"""
    
    print("🚀 Log Feeding Service Demo")
    print("=" * 50)
    
    # Setup service with filters
    primary_db = InMemoryDatabase()
    replica_db = InMemoryDatabase()
    
    # Create filters - only process INFO level and above for "user-service"
    filters = [
        LevelFilter(LogLevel.INFO),
        ServiceFilter(["user-service", "payment-service", "order-service"])
    ]
    
    service = LogFeedingService(
        primary_db=primary_db,
        replica_dbs=[replica_db],
        replication_strategy=MasterSlaveReplication(),
        id_generator=SnowflakeIDGenerator(machine_id=1),
        filters=filters
    )
    
    # Create API
    api = LogFeedingAPI(service)
    
    print("\n1. Ingesting logs...")
    
    # Test log ingestion
    test_logs = [
        {
            "level": "INFO",
            "service_name": "user-service",
            "message": "User login successful",
            "metadata": {"user_id": "12345", "ip": "192.168.1.1"},
            "correlation_id": "req-001"
        },
        {
            "level": "DEBUG",  # Will be filtered out
            "service_name": "user-service",
            "message": "Debug info",
            "metadata": {}
        },
        {
            "level": "ERROR",
            "service_name": "payment-service",
            "message": "Payment processing failed",
            "metadata": {"transaction_id": "txn-456", "amount": 99.99},
            "correlation_id": "req-002"
        },
        {
            "level": "WARN",
            "service_name": "unknown-service",  # Will be filtered out
            "message": "Unknown service warning",
            "metadata": {}
        }
    ]
    
    ingested_ids = []
    for log_data in test_logs:
        response = api.post_log(log_data)
        print(f"  • {log_data['level']} from {log_data['service_name']}: {response}")
        if response.get("status") == 201:
            ingested_ids.append(response["log_id"])
    
    print(f"\n2. Service Metrics:")
    metrics_response = api.get_metrics()
    for key, value in metrics_response["metrics"].items():
        print(f"  • {key}: {value}")
    
    print(f"\n3. Querying logs...")
    
    # Query all logs
    all_logs = api.get_logs({})
    print(f"  • All logs: {all_logs['count']} found")
    
    # Query by service
    user_logs = api.get_logs({"service_name": "user-service"})
    print(f"  • User service logs: {user_logs['count']} found")
    
    # Query by level
    error_logs = api.get_logs({"level": "ERROR"})
    print(f"  • Error logs: {error_logs['count']} found")
    
    # Query by correlation ID
    corr_logs = api.get_logs({"correlation_id": "req-001"})
    print(f"  • Correlation ID req-001: {corr_logs['count']} found")
    
    print(f"\n4. Fetching specific log:")
    if ingested_ids:
        log_detail = api.get_log_by_id(ingested_ids[0])
        if log_detail.get("status") == 200:
            log = log_detail["log"]
            print(f"  • ID: {log['id']}")
            print(f"  • Level: {log['level']}")
            print(f"  • Service: {log['service_name']}")
            print(f"  • Message: {log['message']}")
            print(f"  • Timestamp: {log['timestamp']}")
    
    print(f"\n✅ Demo completed successfully!")
    
    return service, api


if __name__ == "__main__":
    # Run the demo
    service, api = demo_log_feeding_service()
    
    print(f"\n" + "=" * 50)
    print("🎯 Key Design Decisions:")
    print("1. Strategy Pattern for replication strategies")
    print("2. Filter Chain for log processing")
    print("3. Pluggable ID generation (UUID vs Snowflake)")
    print("4. Abstract database interface for different storage backends")
    print("5. RESTful API design following best practices")
    print("6. Comprehensive indexing for efficient queries")
    print("7. Thread-safe operations with proper locking")
    print("8. Metrics collection for monitoring")