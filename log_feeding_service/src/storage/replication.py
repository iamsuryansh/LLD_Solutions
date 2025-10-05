"""
Replication strategies for Log Feeding Service
"""

from abc import ABC, abstractmethod
from typing import List
from .database_interface import DatabaseInterface
from ..models import LogEntry


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