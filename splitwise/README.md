# Splitwise Low Level Design - Enhanced User & Group-Centric Solution

## 📋 Problem Statement

Design a comprehensive **expense-sharing system** like Splitwise with advanced user management, group functionality, and flexible expense splitting capabilities.

## 🎯 Enhanced Requirements Covered

### Functional Requirements
- ✅ **User Management**: Add users with profiles (name, email, phone)
- ✅ **Group Management**: Create groups, add/remove users from groups
- ✅ **Flexible Expense Splitting**: Support for equal, exact, percentage, and mixed splits
- ✅ **Multi-User Expense Addition**: Pass list of users with various split parameters
- ✅ **Group-Specific Tracking**: Track balances within groups and overall
- ✅ **Advanced Settlement System**: Settle debts with group context
- ✅ **Comprehensive Reporting**: User, group, and system-wide balance views
- ✅ **Expense Categories**: Organize expenses by categories (Food, Travel, etc.)

### Non-Functional Requirements
- ✅ **Clean Architecture**: Separation of concerns with dedicated managers
- ✅ **Extensible Design**: Easy to add new split types and features
- ✅ **Robust Validation**: Comprehensive input validation and error handling
- ✅ **Group Context**: All operations can be performed within group scope
- ✅ **Flexible API**: Multiple methods for different split scenarios

## 🏗️ Enhanced System Architecture

### Class Hierarchy
```
ExpenseManager (Main Controller)
├── User (Enhanced with group memberships)
├── Group (Group management with members and expenses)
├── Expense (Flexible with SplitDetail objects)
├── SplitDetail (Individual user split configuration)
├── SplitValidator (Validation logic)
├── BalanceManager (Group-aware balance tracking)
└── GroupManager (Dedicated group operations)
```

### Key Design Patterns Used
1. **Strategy Pattern**: Different split calculation approaches
2. **Composite Pattern**: Mixed split types within single expense
3. **Manager Pattern**: Dedicated managers for different concerns
4. **Data Class Pattern**: Clean data structures with SplitDetail
5. **Single Responsibility**: Each class has one clear purpose

## 🔄 Enhanced System Flow

1. **User Registration**: Add users with detailed profiles
2. **Group Creation**: Create groups and manage memberships
3. **Expense Addition**: Add expenses with flexible participant selection
4. **Split Calculation**: Support equal, exact, percentage, and mixed splits
5. **Balance Tracking**: Maintain group-specific and overall balances
6. **Settlement**: Users can settle debts within group context
7. **Reporting**: Comprehensive balance and group summaries

## 💡 New API Methods for Enhanced Functionality

### User & Group Management
```python
# User management
manager.add_user("alice", "Alice Johnson", "alice@email.com", "555-0101")

# Group creation and management
group = manager.create_group("Roommates", "Shared apartment expenses", "alice")
manager.add_users_to_group(group.group_id, ["alice", "bob", "charlie"])
```

### Flexible Expense Addition

#### 1. **Equal Split** (Enhanced)
```python
manager.add_expense_equal_split(
    amount=150.0,
    paid_by_id="alice",
    participant_ids=["alice", "bob", "charlie"],
    description="Grocery shopping",
    category=ExpenseCategory.FOOD,
    group_id="group_12345"
)
```

#### 2. **Exact Split** (New Method)
```python
manager.add_expense_exact_split(
    amount=200.0,
    paid_by_id="bob",
    user_amounts={"alice": 80.0, "bob": 60.0, "diana": 60.0},
    description="Hotel booking",
    category=ExpenseCategory.TRAVEL,
    group_id="group_67890"
)
```

#### 3. **Percentage Split** (New Method)
```python
manager.add_expense_percent_split(
    amount=300.0,
    paid_by_id="charlie",
    user_percentages={"alice": 40.0, "bob": 35.0, "charlie": 25.0},
    description="Utilities bill",
    category=ExpenseCategory.UTILITIES,
    group_id="group_12345"
)
```

#### 4. **Mixed Split** (Advanced New Feature)
```python
manager.add_expense_mixed_split(
    amount=240.0,
    paid_by_id="diana",
    split_configs=[
        {"user_id": "alice", "type": "PERCENT", "percentage": 50.0},  # $120
        {"user_id": "bob", "type": "EXACT", "amount": 80.0},           # $80
        {"user_id": "diana", "type": "EQUAL"}                        # $40 (remaining)
    ],
    description="Restaurant dinner",
    category=ExpenseCategory.FOOD,
    group_id="group_67890"
)
```

### Enhanced Balance & Settlement Operations

```python
# Group-specific settlements
manager.settle_up("bob", "alice", 50.0, group_id="group_12345")

# Enhanced balance views
manager.show_user_balances("alice", group_id="group_12345")  # Group-specific
manager.show_user_balances("alice")                          # Overall balances
manager.show_group_balances("group_12345")                  # All group balances
manager.show_group_summary("group_12345")                   # Comprehensive group info
```

## 💡 Interview Discussion Points

### 1. **Enhanced Architecture Considerations**
- **Group-Aware Design**: Dual balance tracking (overall + group-specific)
- **Flexible Split System**: Support for mixed split types in single expense
- **Manager Pattern**: Dedicated managers for users, groups, expenses, balances
- **Data Validation**: Comprehensive validation for complex split scenarios

### 2. **Enhanced Database Schema Design**
```sql
-- Users table (enhanced)
Users: 
  user_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  phone VARCHAR(20),
  created_at TIMESTAMP,
  is_active BOOLEAN DEFAULT true

-- Groups table (new)
Groups:
  group_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  created_by VARCHAR(50) REFERENCES Users(user_id),
  created_at TIMESTAMP,
  is_active BOOLEAN DEFAULT true

-- Group memberships (new)
GroupMemberships:
  group_id VARCHAR(50) REFERENCES Groups(group_id),
  user_id VARCHAR(50) REFERENCES Users(user_id),
  joined_at TIMESTAMP,
  PRIMARY KEY (group_id, user_id)

-- Enhanced expenses table
Expenses:
  expense_id VARCHAR(50) PRIMARY KEY,
  amount DECIMAL(10,2) NOT NULL,
  paid_by_user_id VARCHAR(50) REFERENCES Users(user_id),
  description TEXT,
  category VARCHAR(50),
  group_id VARCHAR(50) REFERENCES Groups(group_id),
  created_at TIMESTAMP

-- Enhanced splits table
ExpenseSplits:
  expense_id VARCHAR(50) REFERENCES Expenses(expense_id),
  user_id VARCHAR(50) REFERENCES Users(user_id),
  split_type VARCHAR(20) NOT NULL, -- EQUAL, EXACT, PERCENT
  split_value DECIMAL(10,2),       -- amount or percentage
  calculated_amount DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (expense_id, user_id)

-- Enhanced balances (now with group context)
Balances:
  from_user_id VARCHAR(50) REFERENCES Users(user_id),
  to_user_id VARCHAR(50) REFERENCES Users(user_id),
  amount DECIMAL(10,2) NOT NULL,
  group_id VARCHAR(50) REFERENCES Groups(group_id), -- nullable for overall
  updated_at TIMESTAMP,
  PRIMARY KEY (from_user_id, to_user_id, group_id)
```

### 3. **Advanced Features Implemented**
- ✅ **Groups**: Full group management with membership controls
- ✅ **Categories**: Food, Travel, Entertainment, Utilities, Shopping
- ✅ **Mixed Splits**: Multiple split types within single expense
- ✅ **Group Context**: All operations support group-specific context
- ✅ **Enhanced Reporting**: Comprehensive balance and group summaries
- ✅ **Flexible APIs**: Multiple methods for different split scenarios

### 4. **Enhanced Edge Cases Handled**
- ✅ Floating point precision in all calculations
- ✅ Mixed split validation (exact + percentage + equal)
- ✅ Group membership validation for expenses
- ✅ Payer must be included in split validation
- ✅ Comprehensive input validation for all operations
- ✅ Group-specific vs overall balance consistency
- ✅ Settlement validation against actual debts

## 🚀 Running the Enhanced Implementation

```python
# Run the comprehensive demo
python splitwise_lld.py

# Expected output shows:
# 1. User creation and group formation
# 2. Various expense splitting scenarios (equal, exact, percentage, mixed)
# 3. Group-specific balance tracking
# 4. Settlement demonstrations
# 5. Comprehensive reporting features
```

## 🧪 Enhanced Test Scenarios

### Test Case 1: Group Creation and Management
```python
# Create users and group
manager.add_user("alice", "Alice", "alice@email.com")
group = manager.create_group("Roommates", "Shared expenses")
manager.add_users_to_group(group.group_id, ["alice", "bob"])

# Expected: Group created with 2 members
```

### Test Case 2: Mixed Split Expense
```python
# Complex expense with multiple split types
manager.add_expense_mixed_split(
    amount=300.0,
    paid_by_id="alice",
    split_configs=[
        {"user_id": "alice", "type": "PERCENT", "percentage": 50.0},  # $150
        {"user_id": "bob", "type": "EXACT", "amount": 100.0},         # $100  
        {"user_id": "charlie", "type": "EQUAL"}                     # $50
    ]
)

# Expected: Alice owes $0, Bob owes Alice $100, Charlie owes Alice $50
```

### Test Case 3: Group-Specific Settlements
```python
# Settle within group context
manager.settle_up("bob", "alice", 50.0, group_id="group_123")

# Expected: Group balance updated, overall balance also updated
```

## 📊 Enhanced Complexity Analysis

| Operation | Time Complexity | Space Complexity | Notes |
|-----------|----------------|------------------|-------|
| Add User | O(1) | O(1) | Hash table lookup |
| Create Group | O(1) | O(1) | Group creation |
| Add to Group | O(1) | O(1) | Member addition |
| Add Expense (any split) | O(n) | O(n) | n = participants |
| Calculate Mixed Split | O(n) | O(1) | Linear scan by type |
| Show Group Balances | O(n²) | O(1) | All pairs in group |
| Settle Payment | O(1) | O(1) | Direct hash lookup |
| Group Summary | O(n + m) | O(1) | n=members, m=expenses |

Where n = number of participants/members, m = number of expenses

## 🔧 Extensions for Advanced Interview

### 1. **Simplify Debts Algorithm**
```python
# Minimize number of transactions
# Instead of: A->B $10, B->C $10
# Optimize to: A->C $10
```

### 2. **Group Management**
```python
class Group:
    def __init__(self, group_id, name, members):
        self.group_id = group_id
        self.name = name
        self.members = members  # List of User objects
```

### 3. **Expense Categories**
```python
class ExpenseCategory(Enum):
    FOOD = "FOOD"
    TRAVEL = "TRAVEL"
    ENTERTAINMENT = "ENTERTAINMENT"
    UTILITIES = "UTILITIES"
```

### 4. **REST API Endpoints**
```python
# Potential API design
POST /users                    # Create user
POST /expenses                 # Add expense
GET /users/{id}/balances      # Get user balances
POST /settlements             # Settle payment
GET /users/{id}/expenses      # Get user expenses
```

## 🎤 Interview Presentation Tips

1. **Start Simple**: Begin with basic classes and requirements
2. **Build Incrementally**: Add features one by one
3. **Explain Design Choices**: Why abstract Split class?
4. **Handle Edge Cases**: Show validation logic
5. **Discuss Improvements**: Database, API, scaling
6. **Time Management**: Core features first, extensions later

## 🔍 Follow-up Questions to Prepare For

1. **How would you handle concurrent updates to balances?**
   - Database transactions, optimistic locking

2. **How to handle different currencies?**
   - Currency field in Expense, exchange rate service

3. **How to optimize for read-heavy workload?**
   - Caching, read replicas, denormalized balance tables

4. **How to ensure data consistency?**
   - ACID transactions, event sourcing for audit trail

5. **How to handle very large friend groups?**
   - Pagination, batch processing, async calculations

---

## 🌟 Key Enhancements Summary

### 🆕 **New Features Added:**
1. ✅ **Group Management System** - Full CRUD operations for groups
2. ✅ **Enhanced User Profiles** - Phone, group memberships, profiles
3. ✅ **Flexible Split Methods** - 4 different ways to add expenses
4. ✅ **Mixed Split Support** - Multiple split types in single expense
5. ✅ **Group-Aware Balances** - Separate tracking for group vs overall
6. ✅ **Advanced Reporting** - Group summaries, user reports, system overview
7. ✅ **Expense Categories** - Organized expense management
8. ✅ **Robust Validation** - Comprehensive input validation and error handling

### 🔧 **Technical Improvements:**
1. ✅ **Better Architecture** - Separated concerns with dedicated managers
2. ✅ **Clean Data Structures** - SplitDetail dataclass for type safety
3. ✅ **Enhanced APIs** - Multiple methods for different use cases
4. ✅ **Comprehensive Demo** - Real-world scenarios demonstration
5. ✅ **Production Ready** - Error handling, validation, edge cases

### 🎤 **Enhanced Interview Discussion Points:**

#### Technical Architecture Questions:
1. **How does the group-aware balance system work?**
   - Dual tracking: overall + group-specific balances
   - Hierarchical balance resolution

2. **How do you handle mixed split validation?**
   - Pre-validation of individual split types
   - Total amount reconciliation after calculation

3. **What's the strategy for handling complex group scenarios?**
   - Member removal with existing balances
   - Group merging and splitting

#### System Design Questions:
1. **How would you scale this for 10M users and 1000 groups each?**
   - Database sharding by user_id or group_id
   - Caching layer for frequently accessed balances
   - Read replicas for balance queries

2. **How to handle eventual consistency in distributed environment?**
   - Event sourcing for expense additions
   - SAGA pattern for complex multi-step operations
   - Compensation transactions for failed settlements

*This enhanced implementation provides a production-ready foundation that handles complex real-world scenarios while maintaining clean, maintainable code suitable for senior-level interviews.*