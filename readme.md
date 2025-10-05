# Python Low-Level Design Practice

This repository contains implementations of various low-level design problems to practice system design concepts using Python. Each problem is implemented with **clean, modular architecture** following SOLID principles.

## Problems Implemented

### 1. Splitwise - Expense Sharing Application 
**Location**: `splitwise/` (Modular Architecture)

A comprehensive expense-sharing system that allows users to split bills and track balances between friends.

#### 🏗️ Modular Architecture:
```
splitwise/
├── src/
│   ├── models/          # User, Group, Expense, SplitDetail models
│   ├── services/        # ExpenseManager, BalanceManager, GroupManager  
│   ├── validators/      # SplitValidator for validation logic
│   └── enums/          # SplitType, ExpenseCategory enums
├── demo/               # Comprehensive demo scenarios
└── main.py            # Main entry point with backward compatibility
```

#### Key Features:
- **User Management**: Create and manage user accounts with profiles
- **Group Management**: Create groups and manage group memberships  
- **Flexible Expense Splitting**: Support for equal, exact, percentage, and mixed splits
- **Balance Tracking**: Track balances between individual users and within groups
- **Settlement System**: Process payments and update balances with group context
- **Comprehensive Reporting**: Generate balance summaries and group statistics

#### Enhanced Functionality:
- **User-Centric Design**: All operations center around user profiles and relationships
- **Group-Aware Operations**: Expenses and settlements are tracked within group contexts
- **Advanced Split Types**: 
  - Equal: Split amount equally among participants
  - Exact: Specify exact amounts for each participant  
  - Percentage: Split based on percentages (auto-calculates remaining)
  - Mixed: Combine different split types in one expense
- **Smart Validation**: Comprehensive validation for splits, users, and amounts
- **Category Organization**: Organize expenses by categories (Food, Travel, Utilities, etc.)

#### Demo Usage:
```bash
cd splitwise
python3 main.py
```

### 2. Log Feeding Service - Distributed Log Collection System
**Location**: `log_feeding_service/` (Modular Architecture)

A high-throughput log collection and management system designed for distributed environments.

#### 🏗️ Modular Architecture:
```
log_feeding_service/
├── src/
│   ├── models/          # LogEntry, LogLevel enums
│   ├── storage/         # DatabaseInterface, InMemoryDatabase, Replication
│   ├── services/        # LogFeedingService, ScalingStrategies
│   ├── filters/         # LogFilter, LevelFilter, ServiceFilter, etc.
│   └── api/            # REST API handlers and routes
├── demo/               # Comprehensive demo scenarios
└── main.py            # Main entry point with backward compatibility
```

#### Key Features:
- **High-Throughput Ingestion**: Handle millions of logs per second
- **Multiple Log Levels**: Support for DEBUG, INFO, WARN, ERROR, FATAL
- **Advanced Filtering**: Filter by service, level, timestamp, keywords
- **Time-Series Storage**: Optimized for time-based queries and retention
- **Replication Strategy**: Master-slave replication for high availability
- **REST API**: RESTful endpoints for log ingestion and querying
- **Scaling Strategies**: Service-based and time-based sharding

#### Architecture Components:
- **Storage Layer**: Abstract database interfaces with in-memory implementation
- **Service Layer**: Core business logic for log management and scaling
- **Filter Layer**: Composable filtering system with multiple filter types
- **API Layer**: Framework-agnostic REST API handlers
- **Replication System**: Master-slave replication with failover support
- **Scaling Layer**: Horizontal scaling with sharding strategies

#### REST API Endpoints:
- `POST /logs` - Ingest single log entry
- `POST /logs/batch` - Batch ingest multiple logs
- `GET /logs` - Query logs with filters (service, level, time range)
- `GET /logs/stats` - Get log statistics and metrics

#### Demo Usage:
```bash
cd log_feeding_service  
python3 main.py
```

## 🎯 Architecture Highlights

### Design Principles Applied:
- **SOLID Principles**: Each class has single responsibility, open for extension, proper abstraction
- **Clean Architecture**: Clear separation between models, services, storage, and presentation layers
- **Dependency Injection**: Services depend on abstractions, not concrete implementations
- **Factory Patterns**: Easy service creation with different configurations
- **Strategy Patterns**: Pluggable algorithms for replication, scaling, and filtering

### Benefits of Modular Design:
- **Maintainability**: Easy to understand, modify, and extend individual components
- **Testability**: Each module can be tested independently with proper mocking
- **Scalability**: Components can be scaled and deployed independently  
- **Reusability**: Modules can be reused across different parts of the system
- **Backward Compatibility**: Main.py files provide compatibility with original single-file designs

## 🚀 Getting Started

1. Clone this repository
2. Navigate to the specific problem directory (`splitwise/` or `log_feeding_service/`)
3. Run `python3 main.py` to see the comprehensive demo
4. Explore the `src/` directory to understand the modular architecture
5. Check out individual modules and their responsibilities

## 🧪 Testing the Modular Design

Both implementations include comprehensive demo scenarios that showcase:

### Splitwise Demo:
- User creation and group management
- All split types (equal, exact, percentage, mixed)
- Balance tracking and settlement processing
- Group-specific operations and reporting

### Log Feeding Service Demo:
- Basic log ingestion and querying
- Batch processing capabilities  
- Replication strategies demonstration
- Advanced filtering scenarios
- REST API usage examples
- Scaling strategies (sharding, load balancing)

## 🔄 Migration Notes

The modular implementations maintain **full backward compatibility** through the `main.py` files, which expose the same interfaces as the original single-file implementations while leveraging the new clean architecture underneath.

## � Future Enhancements

### Enhanced Architecture Features:
- **Event-Driven Architecture**: Implement pub/sub patterns for async operations
- **Microservices Decomposition**: Break into independently deployable services
- **Database Integration**: Add support for real databases (PostgreSQL, MongoDB)
- **Caching Layer**: Add Redis/Memcached for performance optimization
- **Message Queues**: Add Kafka/RabbitMQ for reliable async processing

### Business Logic Enhancements:
- **Authentication & Authorization**: JWT-based security with role-based access
- **Multi-tenancy**: Support for multiple organizations with data isolation
- **Real-time Features**: WebSocket support for live updates
- **Advanced Analytics**: Machine learning for anomaly detection and insights
- **Mobile APIs**: REST/GraphQL APIs optimized for mobile applications

## 🤝 Contributing

Feel free to contribute:
- Additional LLD problems with clean modular architecture
- Enhancements to existing implementations
- Performance optimizations and benchmarks
- Integration tests and documentation improvements

Please ensure all contributions follow the established modular design patterns and include comprehensive documentation.