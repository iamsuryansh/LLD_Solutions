#!/usr/bin/env python3
"""
Comprehensive demo for Log Feeding Service
Demonstrates all major features including:
- Basic log ingestion
- Batch processing  
- Filtering and querying
- Replication strategies
- REST API usage
- Scaling strategies
"""

from datetime import datetime, timedelta
from typing import List

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import (
    LogLevel, LogEntry, LogFeedingService, InMemoryDatabase,
    MasterSlaveReplication, LevelFilter, ServiceFilter, 
    TimeRangeFilter, CompositeFilter, LogAPIHandler, RESTAPIRoutes,
    ServiceBasedSharding, LoadBalancer
)


def demonstrate_basic_functionality():
    """Demo basic log ingestion and querying"""
    print("=== Basic Log Feeding Service Demo ===")
    
    # Setup service
    db = InMemoryDatabase()
    service = LogFeedingService(db)
    
    # Ingest some logs
    print("\n1. Ingesting logs...")
    log_id1 = service.ingest_log(LogLevel.INFO, "User login successful", "auth-service")
    log_id2 = service.ingest_log(LogLevel.ERROR, "Database connection failed", "db-service", 
                               {"error_code": 500, "retry_count": 3})
    log_id3 = service.ingest_log(LogLevel.WARN, "High memory usage detected", "monitor-service")
    log_id4 = service.ingest_log(LogLevel.DEBUG, "Processing user request", "api-service")
    
    print(f"Ingested logs: {log_id1[:8]}..., {log_id2[:8]}..., {log_id3[:8]}..., {log_id4[:8]}...")
    
    # Query logs
    print("\n2. Querying logs by service...")
    auth_logs = service.get_logs_by_service("auth-service")
    print(f"Auth service logs: {len(auth_logs)} entries")
    for log in auth_logs:
        print(f"  - [{log.level.value}] {log.message}")
    
    print("\n3. Querying logs by level...")
    error_logs = service.get_logs_by_level(LogLevel.ERROR)
    print(f"Error logs: {len(error_logs)} entries")
    for log in error_logs:
        print(f"  - [{log.service}] {log.message}")
    
    # Get stats
    print("\n4. Log statistics...")
    stats = service.get_log_stats()
    print(f"Total logs: {stats['total_logs']}")
    print(f"Services: {', '.join(stats['services'])}")
    print(f"Log levels: {', '.join([level.value for level in stats['levels']])}")


def demonstrate_batch_processing():
    """Demo batch log processing"""
    print("\n\n=== Batch Processing Demo ===")
    
    db = InMemoryDatabase()
    service = LogFeedingService(db)
    
    # Batch data
    batch_logs = [
        {"level": "INFO", "message": "Server started", "service": "web-server"},
        {"level": "INFO", "message": "Cache warmed up", "service": "cache-service"},
        {"level": "ERROR", "message": "Payment failed", "service": "payment-service", 
         "metadata": {"user_id": "123", "amount": 99.99}},
        {"level": "WARN", "message": "Rate limit exceeded", "service": "api-service"},
        {"level": "DEBUG", "message": "SQL query executed", "service": "db-service"}
    ]
    
    print(f"Batch ingesting {len(batch_logs)} logs...")
    log_ids = service.batch_ingest_logs(batch_logs)
    print(f"Successfully ingested {len(log_ids)} logs")
    
    # Show recent logs
    print("\nRecent logs (last 60 minutes):")
    recent_logs = service.get_recent_logs(60)
    for log in recent_logs[-3:]:  # Show last 3
        print(f"  - [{log.level.value}] {log.service}: {log.message}")


def demonstrate_replication():
    """Demo replication strategies"""
    print("\n\n=== Replication Demo ===")
    
    # Setup primary and replica databases
    primary_db = InMemoryDatabase()
    replica_db1 = InMemoryDatabase()
    replica_db2 = InMemoryDatabase()
    
    replication_strategy = MasterSlaveReplication()
    service = LogFeedingService(primary_db, replication_strategy, [replica_db1, replica_db2])
    
    print("Ingesting logs with replication...")
    service.ingest_log(LogLevel.INFO, "Replicated log entry", "replication-test")
    
    print(f"Primary DB logs: {len(primary_db.logs)}")
    print(f"Replica 1 logs: {len(replica_db1.logs)}")
    print(f"Replica 2 logs: {len(replica_db2.logs)}")


def demonstrate_filtering():
    """Demo advanced filtering"""
    print("\n\n=== Advanced Filtering Demo ===")
    
    db = InMemoryDatabase()
    service = LogFeedingService(db)
    
    # Add diverse logs
    service.ingest_log(LogLevel.ERROR, "Critical system failure", "core-service")
    service.ingest_log(LogLevel.WARN, "Memory usage high", "monitor-service")
    service.ingest_log(LogLevel.INFO, "User authenticated", "auth-service")
    service.ingest_log(LogLevel.ERROR, "Database timeout", "db-service")
    service.ingest_log(LogLevel.DEBUG, "Cache hit", "cache-service")
    
    all_logs = service.get_recent_logs(60)
    print(f"Total logs: {len(all_logs)}")
    
    # Level filtering
    print("\n1. Level filtering (ERROR only):")
    level_filter = LevelFilter({LogLevel.ERROR})
    error_logs = level_filter.apply(all_logs)
    for log in error_logs:
        print(f"  - {log.service}: {log.message}")
    
    # Service filtering
    print("\n2. Service filtering (services ending with '-service'):")
    service_filter = ServiceFilter({"auth-service", "db-service"})
    service_logs = service_filter.apply(all_logs)
    for log in service_logs:
        print(f"  - [{log.level.value}] {log.message}")
    
    # Composite filtering (ERROR level AND specific services)
    print("\n3. Composite filtering (ERROR + specific services):")
    composite_filter = CompositeFilter([level_filter, service_filter])
    filtered_logs = composite_filter.apply(all_logs)
    for log in filtered_logs:
        print(f"  - {log.service}: {log.message}")


def demonstrate_rest_api():
    """Demo REST API functionality"""
    print("\n\n=== REST API Demo ===")
    
    db = InMemoryDatabase()
    service = LogFeedingService(db)
    api_handler = LogAPIHandler(service)
    api_routes = RESTAPIRoutes(api_handler)
    
    # Test POST /logs
    print("1. Testing POST /logs")
    post_data = {
        "level": "ERROR",
        "message": "API endpoint failed",
        "service": "web-api",
        "metadata": {"status_code": 500, "endpoint": "/users"}
    }
    response = api_routes.handle_request("POST", "/logs", post_data)
    print(f"Response: {response['status']} - {response['message']}")
    
    # Test batch POST
    print("\n2. Testing POST /logs/batch")
    batch_data = {
        "logs": [
            {"level": "INFO", "message": "Request started", "service": "web-api"},
            {"level": "INFO", "message": "Request completed", "service": "web-api"}
        ]
    }
    response = api_routes.handle_request("POST", "/logs/batch", batch_data)
    print(f"Response: {response['status']} - Ingested {response['count']} logs")
    
    # Test GET /logs with filters
    print("\n3. Testing GET /logs with filters")
    query_params = {
        "service": "web-api",
        "level": "ERROR",
        "limit": "10",
        "page": "1"
    }
    response = api_routes.handle_request("GET", "/logs", query_params=query_params)
    print(f"Response: {response['status']} - Found {response['total']} logs")
    
    # Test GET /logs/stats
    print("\n4. Testing GET /logs/stats")
    response = api_routes.handle_request("GET", "/logs/stats")
    print(f"Response: {response['status']}")
    if response['status'] == 'success':
        print(f"Stats: {response['stats']}")
    else:
        print(f"Error: {response.get('message', 'Unknown error')}")


def demonstrate_scaling():
    """Demo scaling strategies"""
    print("\n\n=== Scaling Strategies Demo ===")
    
    # Service-based sharding
    print("1. Service-based sharding:")
    shard1_db = InMemoryDatabase()
    shard2_db = InMemoryDatabase()
    
    shard_map = {
        "user-service": shard1_db,
        "order-service": shard2_db
    }
    sharding_strategy = ServiceBasedSharding(shard_map)
    
    # Create sample log entries
    user_log = LogEntry(LogLevel.INFO, "User created", "user-service")
    order_log = LogEntry(LogLevel.INFO, "Order placed", "order-service")
    
    user_db = sharding_strategy.route_log(user_log)
    order_db = sharding_strategy.route_log(order_log)
    
    print(f"User log routed to: {'Shard 1' if user_db == shard1_db else 'Shard 2'}")
    print(f"Order log routed to: {'Shard 1' if order_db == shard1_db else 'Shard 2'}")
    
    # Load balancing
    print("\n2. Load balancing:")
    service1 = LogFeedingService(InMemoryDatabase())
    service2 = LogFeedingService(InMemoryDatabase())
    service3 = LogFeedingService(InMemoryDatabase())
    
    load_balancer = LoadBalancer([service1, service2, service3])
    
    print("Distributing requests across services:")
    for i in range(6):
        selected_service = load_balancer.get_next_service()
        service_id = [service1, service2, service3].index(selected_service) + 1
        print(f"  Request {i+1} -> Service {service_id}")


def run_comprehensive_demo():
    """Run all demo scenarios"""
    print("🚀 Log Feeding Service - Comprehensive Demo")
    print("=" * 50)
    
    try:
        demonstrate_basic_functionality()
        demonstrate_batch_processing()
        demonstrate_replication()
        demonstrate_filtering()
        demonstrate_rest_api()
        demonstrate_scaling()
        
        print("\n\n✅ All demos completed successfully!")
        print("\nKey Features Demonstrated:")
        print("- Basic log ingestion and querying")
        print("- Batch processing capabilities")
        print("- Master-slave replication")
        print("- Advanced filtering (level, service, time, composite)")
        print("- RESTful API endpoints")
        print("- Scaling strategies (sharding, load balancing)")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    run_comprehensive_demo()