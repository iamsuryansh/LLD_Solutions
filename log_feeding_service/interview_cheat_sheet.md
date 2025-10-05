# Log Feeding Service - Interview Cheat Sheet

## 🎯 Quick Problem Summary (2 min)

**"Design a distributed log collection system like Fluentd or CloudWatch Logs"**

### Key Features:
- Multi-service log ingestion with different levels
- Unique ID generation (Snowflake-like)  
- Filtering system (level, service, time, correlation)
- RESTful APIs with proper HTTP practices
- Database design with replication
- Horizontal scaling strategy

---

## 🏗️ High-Level Architecture (5 min)

```
API Layer → Ingestion Service → Filter Chain → Storage Layer
                                      ↓
Query Engine ← Replication Strategy ← ID Generation
```

### Core Components:
1. **LogFeedingService** - Main orchestrator
2. **DatabaseInterface** - Storage abstraction  
3. **ReplicationStrategy** - Data consistency
4. **LogFilter Chain** - Processing pipeline
5. **IDGenerator** - Unique identification
6. **REST API** - External interface

---

## 💡 Key Design Patterns (3 min)

### 1. **Strategy Pattern**
```python
class ReplicationStrategy(ABC):
    def replicate(self, log, primary, replicas): pass

class MasterSlaveReplication(ReplicationStrategy):
    # Implementation for master-slave
```

### 2. **Chain of Responsibility** 
```python
class LogFilter(ABC):
    def should_process(self, log_entry): pass

# LevelFilter → ServiceFilter → CompositeFilter
```

### 3. **Abstract Factory**
```python
class DatabaseInterface(ABC):
    def store_log(self): pass
    def query_logs(self): pass
    
# InMemoryDB, PostgresDB, InfluxDB implementations
```

---

## 📊 Database Design (8 min)

### Primary Choice: **Time-Series DB** (InfluxDB/TimescaleDB)
```sql
CREATE TABLE logs (
    id VARCHAR(50) PRIMARY KEY,           -- Snowflake ID
    timestamp TIMESTAMPTZ NOT NULL,      -- Main query dimension
    level VARCHAR(10) NOT NULL,          -- DEBUG/INFO/WARN/ERROR/FATAL
    service_name VARCHAR(100) NOT NULL,  -- Microservice identifier
    message TEXT NOT NULL,               -- Log content
    metadata JSONB,                      -- Flexible additional data
    correlation_id VARCHAR(50)           -- Request tracing
);

-- Critical Indexes
CREATE INDEX idx_timestamp ON logs(timestamp);
CREATE INDEX idx_service_level ON logs(service_name, level);  
CREATE INDEX idx_correlation ON logs(correlation_id);
```

### Why Time-Series?
- **Optimized for time-based queries** (90% of log queries are time-range)
- **Automatic partitioning** by time periods
- **Built-in compression** for old data
- **Efficient aggregations** (count, avg response times)

### Alternative: **NoSQL (MongoDB/DynamoDB)**
- Better for flexible schema changes
- Horizontal scaling built-in
- JSON-native metadata storage

---

## 🌐 REST API Design (8 min)

### 1. **Log Ingestion**
```http
POST /api/v1/logs
{
  "level": "ERROR",
  "service_name": "payment-service",
  "message": "Payment failed", 
  "metadata": {"transaction_id": "txn-123"},
  "correlation_id": "req-abc"
}
→ 201 Created: {"log_id": "1704110400000-1-123"}
```

### 2. **Log Querying** 
```http
GET /api/v1/logs?service_name=payment-service&level=ERROR&start_time=2024-01-01T00:00:00Z&limit=50
→ 200 OK: {"logs": [...], "count": 25}
```

### 3. **Specific Log**
```http
GET /api/v1/logs/{log_id}
→ 200 OK: {"log": {...}}
```

### REST Best Practices:
- ✅ **Proper HTTP status codes** (201 for creation, 404 for not found)
- ✅ **Resource-based URLs** (/logs not /getLogs)
- ✅ **Query parameters** for filtering (not POST body)
- ✅ **Consistent response format** with metadata
- ✅ **API versioning** (/v1/)
- ✅ **Error handling** with meaningful messages

---

## 🆔 ID Generation Strategy (5 min)

### **Snowflake-like ID**: `timestamp-machine_id-sequence`

```python
class SnowflakeIDGenerator:
    def generate_id(self, log_entry):
        timestamp = int(time.time() * 1000)  # milliseconds
        return f"{timestamp}-{self.machine_id}-{self.sequence}"
```

### Benefits:
- **Time-sortable** - Natural ordering by creation time
- **Distributed** - No central coordination needed
- **Unique** - Machine ID + sequence prevents collisions
- **Efficient** - No database roundtrip for ID generation

### Alternative: **UUID4**
- Simpler implementation
- Not time-sortable
- 128-bit vs 64-bit overhead

---

## ⚡ Scaling Strategy (10 min)

### 1. **Horizontal Scaling**

#### Ingestion Layer:
```
Load Balancer
    ├── Ingestion Service 1
    ├── Ingestion Service 2  
    └── Ingestion Service N
```

#### Database Sharding:
- **By Time**: 2024-Q1, 2024-Q2 partitions
- **By Service**: payment-logs, user-logs, order-logs
- **Hybrid**: Time + Service hash

### 2. **Caching Strategy**
```python
# Query Result Caching
@cache(ttl=300)  # 5 minutes
def get_error_logs_last_hour(service_name):
    return db.query_logs({
        "service_name": service_name,
        "level": "ERROR", 
        "start_time": datetime.now() - timedelta(hours=1)
    })
```

### 3. **Stream Processing**
```
Services → Kafka → Log Ingestion → Database
                       ↓
                   Stream Processor (Flink)
                       ↓
                   Real-time Alerts
```

### 4. **Storage Tiering**
- **Hot Storage** (SSD): Last 7 days - Sub-second queries
- **Warm Storage** (HDD): 7-90 days - Few seconds queries  
- **Cold Storage** (Archive): 90+ days - Minutes for queries

---

## 🔧 Filtering System (5 min)

### Chain of Responsibility Pattern:
```python
filters = [
    LevelFilter(LogLevel.INFO),           # Only INFO and above
    ServiceFilter(["payment", "user"]),   # Allowed services
    RateLimitFilter(1000)                 # Max logs per minute
]

for filter in filters:
    if not filter.should_process(log_entry):
        return  # Skip processing
```

### Filter Types:
1. **LevelFilter** - Minimum log level threshold
2. **ServiceFilter** - Whitelist/blacklist services
3. **RateLimitFilter** - Prevent spam from services
4. **ContentFilter** - Block sensitive information
5. **CompositeFilter** - Combine multiple filters with AND/OR

---

## 🔄 Replication Strategy (5 min)

### **Master-Slave Replication**:
```python
def replicate(log_entry, primary_db, replica_dbs):
    # 1. Write to primary (synchronous)
    primary_db.store_log(log_entry) 
    
    # 2. Async replication to slaves
    for replica in replica_dbs:
        async_replicate(replica, log_entry)
```

### Trade-offs:
- **Master-Slave**: Simple, eventual consistency, read scaling
- **Multi-Master**: Complex, strong consistency, write scaling
- **Consensus (Raft)**: Strong consistency, partition tolerance

---

## 🎯 Interview Flow (Time Management)

### **Phase 1: Requirements** (5-8 min)
- ✅ Log levels, unique IDs, filtering, APIs
- ✅ Scale: 10K logs/second, 1TB/day
- ✅ Consistency vs Availability trade-offs

### **Phase 2: High-Level Design** (8-10 min)
- ✅ Draw architecture diagram
- ✅ Identify main components
- ✅ Choose database type (time-series)

### **Phase 3: Detailed Design** (25-30 min)
- ✅ Core classes and interfaces  
- ✅ ID generation strategy
- ✅ Filtering system
- ✅ REST API design
- ✅ Database schema

### **Phase 4: Scaling** (8-10 min)
- ✅ Horizontal scaling approach
- ✅ Caching strategy
- ✅ Replication for availability
- ✅ Storage optimization

### **Phase 5: Demo** (5 min)
- ✅ Run the code
- ✅ Show log ingestion
- ✅ Demonstrate filtering
- ✅ Query examples

---

## 💡 Advanced Discussion Points

### **How to handle 100K logs/second?**
1. **Kafka** for buffering and batch processing
2. **Async ingestion** with worker queues  
3. **Database connection pooling**
4. **Batch writes** (1000 logs per transaction)

### **Cross-region deployment?**
1. **Regional clusters** with cross-region replication
2. **Conflict resolution** for multi-master writes
3. **Latency optimization** with regional read replicas

### **Real-time alerting?**
1. **Stream processing** (Flink/Storm) for pattern detection
2. **WebSocket APIs** for real-time log streaming
3. **Circuit breaker** for alert fatigue prevention

---

## ⚠️ Common Pitfalls to Avoid

1. **Don't design for SQL first** - Time-series DBs are better for logs
2. **Don't ignore filtering** - It's critical for performance and cost
3. **Don't forget about IDs** - UUID vs Snowflake has implications
4. **Don't skip replication** - Availability is crucial for logs
5. **Don't ignore REST practices** - Proper HTTP methods and status codes matter
6. **Don't overengineer** - Start simple, then scale

---

*Focus on: Clean abstractions, proper patterns, scalability thinking, and REST best practices!*