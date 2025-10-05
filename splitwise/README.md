# Splitwise Low Level Design - Interview Solution

## 📋 Problem Statement

Design a system like **Splitwise** that allows users to split expenses among friends and track who owes whom.

## 🎯 Core Requirements Covered

### Functional Requirements
- ✅ Add users to the system
- ✅ Add expenses with different split types (Equal, Exact, Percent)
- ✅ Track balances between users
- ✅ Settle debts between users
- ✅ Show individual and overall balances

### Non-Functional Requirements
- ✅ Clean, maintainable code structure
- ✅ Extensible design for new split types
- ✅ Efficient balance calculations
- ✅ Input validation and error handling

## 🏗️ System Architecture

### Class Hierarchy
```
ExpenseManager (Main Controller)
├── User (User Management)
├── Expense (Expense Representation)
├── Split (Abstract Base)
│   ├── EqualSplit
│   ├── ExactSplit
│   └── PercentSplit
├── SplitCalculator (Business Logic)
└── BalanceManager (Balance Tracking)
```

### Key Design Patterns Used
1. **Strategy Pattern**: Different split calculation strategies
2. **Factory Pattern**: Can be extended for split creation
3. **Single Responsibility**: Each class has one clear purpose
4. **Open/Closed Principle**: Easy to add new split types

## 🔄 System Flow

1. **User Registration**: Add users to the system
2. **Expense Addition**: Create expense with split details
3. **Split Calculation**: Calculate individual amounts based on split type
4. **Balance Update**: Update who owes whom
5. **Settlement**: Users can pay each other to settle debts

## 💡 Interview Discussion Points

### 1. **Scalability Considerations**
- **Current**: In-memory storage
- **Production**: Would use database (PostgreSQL/MySQL)
- **Caching**: Redis for frequently accessed balances
- **Microservices**: Split into User Service, Expense Service, Balance Service

### 2. **Database Schema Design**
```sql
Users: user_id, name, email, created_at
Expenses: expense_id, amount, paid_by_user_id, description, created_at
ExpenseSplits: expense_id, user_id, amount, split_type
Balances: from_user_id, to_user_id, amount
```

### 3. **Additional Features to Discuss**
- **Groups**: Multiple friend groups
- **Categories**: Food, Travel, Entertainment
- **Recurring Expenses**: Monthly rent splits
- **Currency Support**: Multi-currency handling
- **Notifications**: Email/SMS for new expenses
- **Mobile App**: REST API design

### 4. **Edge Cases Handled**
- Floating point precision in calculations
- Self-payments (user paying for themselves)
- Negative amounts validation
- Percentage splits not adding to 100%
- Exact splits not matching total amount

## 🚀 How to Run

```python
# Run the demo
python splitwise_lld.py

# Expected output shows:
# 1. Equal split example
# 2. Exact split example  
# 3. Settlement process
# 4. User-specific balances
```

## 🧪 Test Scenarios

### Test Case 1: Equal Split
- 3 users, $120 dinner, paid by Alice
- Expected: Bob owes Alice $40, Charlie owes Alice $40

### Test Case 2: Exact Split
- 3 users, $100 shopping, paid by Bob
- Alice: $40, Bob: $25, Charlie: $35
- Expected: Alice owes Bob $40, Charlie owes Bob $35

### Test Case 3: Settlement
- Bob pays Alice $40
- Expected: Bob's debt to Alice reduces/eliminates

## 📊 Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Add User | O(1) | O(1) |
| Add Expense | O(n) | O(n) |
| Calculate Split | O(n) | O(1) |
| Show Balances | O(n) | O(1) |
| Settle Payment | O(1) | O(1) |

Where n = number of users in the expense

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

*This implementation covers all essential aspects for a 1-hour Splitwise LLD interview while maintaining simplicity and clarity.*