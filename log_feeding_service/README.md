# Log Feeding Service - Modular Architecture

A comprehensive distributed log collection and management system implemented with clean, modular architecture following SOLID principles.

## 🏗️ Architecture Overview

```
log_feeding_service/
├── src/                    # Core implementation
│   ├── models/            # Data models and enums
│   ├── storage/           # Database interfaces and implementations  
│   ├── services/          # Business logic services
│   ├── filters/           # Log filtering functionality
│   └── api/              # REST API layer
├── demo/                  # Demo and example usage
└── main.py               # Main entry point
```

## 🚀 Quick Start

```python
from log_feeding_service.main import create_log_service
from log_feeding_service.src import LogLevel

# Create service
service = create_log_service(use_replication=True)

# Ingest logs
log_id = service.ingest_log(LogLevel.ERROR, "Database failed", "user-service")

# Query logs
recent_errors = service.get_logs_by_level(LogLevel.ERROR)
```

## 🧩 Core Components

### Models
- **LogLevel**: Enum for log severity levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **LogEntry**: Immutable dataclass representing a log entry with metadata

### Storage Layer
- **DatabaseInterface**: Abstract interface for storage backends
- **InMemoryDatabase**: In-memory implementation with querying capabilities
- **ReplicationStrategy**: Abstract base for replication patterns
- **MasterSlaveReplication**: Master-slave replication implementation

### Services
- **LogFeedingService**: Main service orchestrating log operations
- **ScalingStrategy**: Abstract base for sharding and partitioning
- **ServiceBasedSharding**: Route logs by service name
- **TimeBasedSharding**: Route logs by timestamp
- **LoadBalancer**: Round-robin load distribution

### Filters
- **LevelFilter**: Filter by log levels
- **ServiceFilter**: Filter by service names  
- **TimeRangeFilter**: Filter by time ranges
- **KeywordFilter**: Filter by message keywords
- **CompositeFilter**: Combine multiple filters with AND logic

### API Layer
- **LogAPIHandler**: Business logic for REST endpoints
- **RESTAPIRoutes**: Framework-agnostic route definitions

## 📊 REST API Endpoints

### POST /logs
Ingest single log entry
```json
{
  "level": "ERROR",
  "message": "Database connection failed",
  "service": "user-service", 
  "metadata": {"error_code": 500}
}
```

### POST /logs/batch  
Batch ingest multiple logs
```json
{
  "logs": [
    {"level": "INFO", "message": "...", "service": "..."},
    {"level": "ERROR", "message": "...", "service": "..."}
  ]
}
```

### GET /logs
Query logs with filters
```
GET /logs?service=user-service&level=ERROR&start_time=2024-01-01T00:00:00&limit=100&page=1
```

### GET /logs/stats
Get log statistics and metrics

## 🎯 Key Features

### Scalability
- **Horizontal Scaling**: Multiple service instances with load balancing
- **Sharding Strategies**: Service-based and time-based partitioning
- **Replication**: Master-slave replication for high availability

### Filtering & Querying
- Multi-dimensional filtering (level, service, time, keywords)
- Composite filters with AND logic
- Efficient time-range queries
- Pagination support

### Storage Flexibility
- Abstract storage interface supporting multiple backends
- In-memory storage for development/testing
- Designed for easy integration with time-series databases

### Production Ready
- Comprehensive error handling
- Structured logging with metadata
- REST API with proper HTTP status codes
- Batch processing for high throughput

## 🔧 Design Patterns Applied

- **Strategy Pattern**: Pluggable replication and scaling strategies
- **Factory Pattern**: Service creation with different configurations  
- **Repository Pattern**: Abstract storage interface
- **Composite Pattern**: Combining multiple filters
- **Template Method**: Abstract filter base class

## 🎮 Running the Demo

```bash
cd log_feeding_service
python main.py
```

The demo showcases:
- Basic log ingestion and querying
- Batch processing capabilities
- Replication strategies
- Advanced filtering scenarios
- REST API usage examples
- Scaling strategies demonstration

## 📈 Scaling Considerations

### Database Choices
- **Time-Series DB**: InfluxDB, TimescaleDB for time-based queries
- **NoSQL**: MongoDB, Cassandra for high write throughput
- **Search Engine**: Elasticsearch for complex text queries

### Deployment Patterns
- **Microservices**: Deploy as independent service
- **Event Streaming**: Kafka/Pulsar for async log processing  
- **Containerization**: Docker containers with Kubernetes orchestration

### Performance Optimization
- **Batch Processing**: Group multiple logs for efficient writes
- **Async Processing**: Non-blocking log ingestion
- **Connection Pooling**: Reuse database connections
- **Caching**: Redis for frequently accessed data

## 🧪 Testing

The modular architecture enables easy unit testing:
- Mock storage interfaces for isolated service testing
- Test filters independently with sample data
- API layer testing with mock services
- Integration tests with in-memory storage

## 🔄 Migration from Single File

The main.py provides full backward compatibility with the original monolithic implementation while leveraging the new modular architecture underneath.

---

## 🏗️ System Architecture

### Core Components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │  Log Ingestion  │    │   Filter Chain  │
│   (REST APIs)   │───▶│    Service      │───▶│   (Validation)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Query Engine  │    │  Storage Layer  │    │  ID Generation  │
│   (Search/Filter)│◀───│  (Database)     │◀───│   (Snowflake)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Replication   │
                       │   (Master/Slave) │
                       └─────────────────┘
```

### Key Classes:

1. **LogEntry**: Core log data model
2. **LogFeedingService**: Main service orchestrator
3. **DatabaseInterface**: Abstract storage layer
4. **ReplicationStrategy**: Data replication handling
5. **LogFilter**: Filtering system (Chain of Responsibility)
6. **IDGenerator**: Unique ID generation strategies
7. **LogFeedingAPI**: RESTful API endpoints

---

## 🔧 Design Patterns Used

### 1. **Strategy Pattern**
- **ReplicationStrategy**: Different replication approaches (Master-Slave, Multi-Master)
- **IDGenerator**: Various ID generation strategies (UUID, Snowflake, Sequential)

### 2. **Chain of Responsibility**
- **LogFilter**: Chained filters for log processing
- Each filter decides whether to process the log entry

### 3. **Abstract Factory**
- **DatabaseInterface**: Pluggable storage backends (In-Memory, SQL, NoSQL, Time-Series)

### 4. **Observer Pattern** (Extensible)
- Can be extended for log streaming and real-time notifications

---

## 📊 Database Design

### Primary Storage Options:

#### 1. **Time-Series Database** (Recommended)
```sql
-- Example: InfluxDB, TimescaleDB
CREATE TABLE logs (
    id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    level VARCHAR(10) NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    source_ip INET,
    correlation_id VARCHAR(50),
    
    -- Indexes for efficient querying
    INDEX idx_timestamp (timestamp),
    INDEX idx_service_level (service_name, level),
    INDEX idx_correlation (correlation_id)
);
```

#### 2. **NoSQL Document Store** (Alternative)
```json
// MongoDB/DynamoDB Schema
{
  "_id": "snowflake_id",
  "timestamp": "2024-01-01T10:30:00Z",
  "level": "ERROR",
  "service_name": "payment-service",
  "message": "Payment processing failed",
  "metadata": {
    "transaction_id": "txn-12345",
    "user_id": "user-67890",
    "amount": 99.99
  },
  "source_ip": "192.168.1.100",
  "correlation_id": "req-abc123"
}
```

### Indexing Strategy:
- **Primary**: Timestamp (most common query)
- **Secondary**: Service + Level (filtering)
- **Composite**: Correlation ID + Timestamp (tracing)

---

## 🌐 API Design (REST Best Practices)

### 1. **Log Ingestion**
```http
POST /api/v1/logs
Content-Type: application/json

{
  "level": "ERROR",
  "service_name": "payment-service", 
  "message": "Payment processing failed",
  "metadata": {
    "transaction_id": "txn-12345",
    "user_id": "user-67890"
  },
  "correlation_id": "req-abc123"
}

Response: 201 Created
{
  "log_id": "1704110400000-1-123",
  "message": "Log ingested successfully"
}
```

### 2. **Log Querying**
```http
GET /api/v1/logs?service_name=payment-service&level=ERROR&limit=50&start_time=2024-01-01T00:00:00Z

Response: 200 OK
{
  "logs": [...],
  "count": 25,
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 25
  }
}
```

### 3. **Specific Log Retrieval**
```http
GET /api/v1/logs/1704110400000-1-123

Response: 200 OK
{
  "log": {
    "id": "1704110400000-1-123",
    "timestamp": "2024-01-01T10:30:00Z",
    "level": "ERROR",
    ...
  }
}
```

### 4. **Health & Metrics**
```http
GET /api/v1/metrics

Response: 200 OK
{
  "metrics": {
    "logs_received": 10000,
    "logs_processed": 9950,
    "logs_filtered": 50,
    "errors": 5,
    "avg_response_time_ms": 45
  }
}
```

---

## ⚡ Scaling Strategies

### 1. **Horizontal Scaling**
- **Load Balancing**: Multiple ingestion service instances
- **Database Sharding**: Partition by time ranges or service names
- **Microservices**: Separate ingestion, querying, and analytics services

### 2. **Caching Layer**
- **Redis/Memcached**: Cache frequent queries
- **Query Result Caching**: TTL-based caching for dashboard queries
- **Metadata Caching**: Service names, correlation IDs

### 3. **Stream Processing**
- **Apache Kafka**: Message queue for high-throughput ingestion
- **Apache Storm/Flink**: Real-time log processing and alerting
- **Buffer Management**: Batch writes to database

### 4. **Storage Optimization**
- **Data Compression**: Compress old logs
- **Tiered Storage**: Hot (SSD) → Warm (HDD) → Cold (Archive)
- **Retention Policies**: Automatic cleanup of old logs

---

## 🔒 Security Considerations

### 1. **Authentication & Authorization**
```python
# API Key based authentication
headers = {
    "Authorization": "Bearer api_key_12345",
    "X-Service-Name": "payment-service"
}
```

### 2. **Data Privacy**
- **PII Scrubbing**: Remove sensitive information before storage
- **Field Masking**: Mask credit card numbers, passwords
- **Encryption**: Encrypt logs at rest and in transit

### 3. **Rate Limiting**
- **Per-service limits**: Prevent spam from misbehaving services
- **IP-based throttling**: Prevent DoS attacks

---

## 📈 Monitoring & Observability

### Key Metrics:
1. **Throughput**: Logs per second ingested
2. **Latency**: API response times (P50, P95, P99)
3. **Error Rate**: Failed ingestions vs successful
4. **Storage**: Disk usage and growth rate
5. **Query Performance**: Query execution times

### Alerting Rules:
- Error rate > 1% in 5 minutes
- API latency > 200ms for 2 minutes
- Disk usage > 80%
- Replication lag > 1 minute

---

## 🚀 Running the Implementation

```bash
# Navigate to the directory
cd log_feeding_service/

# Run the implementation
python3 log_feeding_service_lld.py

# Expected output:
# - Demo of log ingestion
# - Filtering demonstration  
# - Query examples
# - Metrics display
```

---

## 🎯 Interview Discussion Points

### Technical Decisions:
1. **Why Snowflake IDs?** - Distributed, time-sortable, unique across machines
2. **Filter Chain vs Single Filter?** - Extensible, composable, follows SRP
3. **Replication Strategy?** - Master-slave vs multi-master trade-offs
4. **Database Choice?** - Time-series vs NoSQL vs SQL considerations

### Scalability Questions:
1. **How to handle 100K logs/second?** - Sharding, batching, async processing
2. **Query optimization?** - Indexing strategies, caching, partitioning
3. **Storage growth?** - Retention policies, compression, tiered storage
4. **Multi-region deployment?** - Cross-region replication, consistency models

### Extensions:
1. **Real-time alerting** - Stream processing for critical errors
2. **Log aggregation** - Metrics and dashboards from log data
3. **Full-text search** - Elasticsearch integration for message search
4. **Log streaming** - WebSocket APIs for real-time log tailing

---

*This implementation covers all essential aspects of a production-ready log feeding service while maintaining clean, extensible code suitable for a 60-minute interview.*