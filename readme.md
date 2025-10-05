# Python Low Level Design Practice

This folder contains Python implementations of various Low Level Design problems commonly asked in software engineering interviews.

## 📁 Problems Implemented

### 1. [Splitwise](./splitwise/)
**Difficulty**: Medium  
**Time Required**: 45-60 minutes  
**Key Concepts**: Strategy Pattern, Balance Management, Split Calculations

A expense-sharing application like Splitwise that allows users to split bills among friends and track who owes whom.

**Features Covered**:
- Multiple split types (Equal, Exact, Percentage)
- User balance management
- Debt settlement
- Balance tracking and display

**Interview Focus**: Object-oriented design, design patterns, financial calculations

---

### 2. [Log Feeding Service](./log_feeding_service/)
**Difficulty**: Medium-Hard  
**Time Required**: 60 minutes  
**Key Concepts**: Distributed Systems, REST APIs, Database Design, Scaling, Replication

A distributed log collection and management system similar to Fluentd, Logstash, or CloudWatch Logs that handles log ingestion, storage, filtering, and querying.

**Features Covered**:
- Multi-service log ingestion with different log levels
- Unique ID generation (Snowflake-like algorithm)
- Advanced filtering system (level, service, time-range, correlation)
- RESTful API design following best practices
- Database design with indexing strategies
- Replication strategies for high availability
- Horizontal scaling approach
- Comprehensive metrics and monitoring

**Interview Focus**: System design, scalability, REST APIs, database choices, distributed systems concepts

---

## 🎯 How to Use This Repository

Each problem is contained in its own folder with:
- **Main implementation file** - Single file containing all code with clear class separation
- **README.md** - Detailed problem description, approach, and interview guidance  
- **Interview cheat sheet** - Quick reference for interview presentation

## 📚 Interview Preparation Tips

### General Approach for Any LLD Problem:

1. **Understand Requirements** (5-8 minutes)
   - Ask clarifying questions
   - Identify core entities and relationships
   - Discuss scale and constraints

2. **High-Level Design** (8-10 minutes)
   - Identify main classes and their responsibilities
   - Draw class relationships
   - Choose appropriate design patterns

3. **Detailed Implementation** (25-35 minutes)
   - Start with core classes
   - Add methods and attributes
   - Implement business logic
   - Handle edge cases and validation

4. **Demo and Testing** (5-10 minutes)
   - Walk through example scenarios
   - Show key functionality working
   - Discuss test cases

5. **Extensions and Scale** (5-10 minutes)
   - Database design
   - API design
   - Scaling considerations
   - Additional features

### Code Quality Checklist:
- ✅ Clear class responsibilities (Single Responsibility Principle)
- ✅ Proper abstraction and inheritance
- ✅ Input validation and error handling
- ✅ Meaningful method and variable names
- ✅ Comments explaining complex logic
- ✅ Extensible design for future requirements

## 🚀 Running the Code

Each problem can be run independently:

```bash
# Navigate to specific problem folder
cd splitwise/

# Run the implementation
python3 splitwise_lld.py
```

## 📋 Upcoming Problems

More LLD problems will be added to this repository:

- **Parking Lot System**
- **Library Management System** 
- **Chat Application**
- **Ride Sharing Service**
- **Online Banking System**
- **Food Delivery System**
- **Movie Ticket Booking**
- **Social Media Feed**
- **Distributed Cache System**
- **URL Shortener Service**

## 🔗 Additional Resources

- [Original LLD Problems Repository](../problems/) - Problem statements
- [Design Patterns in Python](../design-patterns/python/) - Common patterns used in LLD
- [System Design Primer](https://github.com/donnemartin/system-design-primer) - For HLD concepts

---

*Each implementation is designed to be completed within a typical 1-hour interview timeframe while covering all essential aspects of the problem.*