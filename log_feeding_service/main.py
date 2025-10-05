"""
Main entry point for Log Feeding Service
Provides backward compatibility with the original single-file design
"""

# Import all components from the modular architecture
from src import *

# For backward compatibility, expose the main service class at module level
__version__ = "2.0.0"
__author__ = "LLD Practice"

def create_log_service(use_replication: bool = False) -> LogFeedingService:
    """
    Factory function to create a configured LogFeedingService instance
    
    Args:
        use_replication: Whether to enable master-slave replication
    
    Returns:
        Configured LogFeedingService instance
    """
    primary_db = InMemoryDatabase()
    
    if use_replication:
        replica_db = InMemoryDatabase()
        replication_strategy = MasterSlaveReplication()
        return LogFeedingService(primary_db, replication_strategy, [replica_db])
    else:
        return LogFeedingService(primary_db)


def main():
    """
    Main entry point - runs the comprehensive demo
    """
    from demo.demo_runner import run_comprehensive_demo
    run_comprehensive_demo()


if __name__ == "__main__":
    main()