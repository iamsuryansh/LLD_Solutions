# Log Feeding Service - Low Level Design

## 🎯 Problem Statement

Design a distributed log collection and management system similar to services like **Fluentd**, **Logstash**, or **AWS CloudWatch Logs**. The system should efficiently handle log ingestion from multiple services, provide filtering capabilities, support various storage backends, and offer RESTful APIs for log querying.

### Key Requirements:

#### Functional Requirements:
1. **Log Ingestion**: Accept logs from multiple services with different log levels
2. **Unique ID Generation**: Assign unique identifiers to each log entry
3. **Log Levels**: Support standard log levels (DEBUG, INFO, WARN, ERROR, FATAL)
4. **Filtering**: Filter logs based on level, service, time range, correlation ID
5. **Storage**: Store logs with proper indexing for efficient retrieval
6. **Querying**: Provide APIs to search and retrieve logs
7. **Replication**: Support data replication for high availability

#### Non-Functional Requirements:
1. **Scalability**: Handle high throughput (thousands of logs per second)
2. **Availability**: 99.9% uptime with replication
3. **Performance**: Sub-100ms response time for queries
4. **Retention**: Configurable log retention policies
5. **Security**: API authentication and authorization
6. **Monitoring**: Metrics and health monitoring

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