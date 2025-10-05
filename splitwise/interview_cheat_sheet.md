# Enhanced Splitwise - Interview Cheat Sheet

## 🎯 Quick Problem Summary (2 min)

**"Design a comprehensive expense sharing app like Splitwise with advanced group management and flexible splitting"**

### Key Enhanced Features:
- ✅ **User Management**: Profiles with group memberships
- ✅ **Group Management**: Create groups, manage memberships  
- ✅ **Flexible Expense Splitting**: Equal, exact, percentage, and mixed splits
- ✅ **Group-Specific Tracking**: Balances within groups and overall
- ✅ **Advanced Settlement**: Group-aware debt settlements
- ✅ **Comprehensive Reporting**: User, group, and system-wide summaries

---

## 🏗️ Enhanced High-Level Architecture (5 min)

```
ExpenseManager (Main Controller)
├── User (Enhanced profiles + groups)
├── Group (Group management)
├── GroupManager (Group operations)
├── Expense (Flexible with SplitDetails)
├── SplitDetail (Individual configurations)
├── SplitValidator (Validation logic)
└── BalanceManager (Group-aware tracking)
```

### Core Components:
1. **User** - Enhanced with group memberships and profiles
2. **Group** - Manages groups of users and group expenses  
3. **Expense** - Flexible expense with SplitDetail objects
4. **SplitDetail** - Individual user split configuration (dataclass)
5. **ExpenseManager** - Main orchestrator with group support
6. **BalanceManager** - Group-aware balance tracking
7. **GroupManager** - Dedicated group operations
8. **SplitValidator** - Comprehensive validation logic

---

## 💡 Enhanced Design Patterns (3 min)

### 1. **Manager Pattern** (New)
```python
class ExpenseManager:    # Main operations
class GroupManager:      # Group-specific operations  
class BalanceManager:    # Balance tracking
```

### 2. **Data Class Pattern** (New)
```python
@dataclass
class SplitDetail:
    user: User
    split_type: SplitType
    value: float = 0.0
    calculated_amount: float = 0.0
```

### 3. **Composite Pattern** (Enhanced)
```python
# Mixed splits in single expense
split_configs = [
    {"user_id": "alice", "type": "PERCENT", "percentage": 50.0},
    {"user_id": "bob", "type": "EXACT", "amount": 80.0},  
    {"user_id": "charlie", "type": "EQUAL"}
]
```

---

## 🚀 Enhanced API Examples (8 min)

### 1. **User & Group Management**
```python
# Enhanced user creation
alice = manager.add_user("alice", "Alice Johnson", "alice@email.com", "555-0101")

# Group creation and management
group = manager.create_group("Roommates", "Shared apartment expenses", "alice")
manager.add_users_to_group(group.group_id, ["alice", "bob", "charlie"])
```

### 2. **Flexible Expense Addition**

#### Equal Split (Enhanced)
```python
manager.add_expense_equal_split(
    amount=150.0,
    paid_by_id="alice", 
    participant_ids=["alice", "bob", "charlie"],
    description="Grocery shopping",
    category=ExpenseCategory.FOOD,
    group_id=group.group_id
)
```

#### Exact Split (New)
```python
manager.add_expense_exact_split(
    amount=200.0,
    paid_by_id="bob",
    user_amounts={"alice": 80.0, "bob": 60.0, "charlie": 60.0},
    description="Hotel booking",
    category=ExpenseCategory.TRAVEL,
    group_id=group.group_id
)
```

#### Percentage Split (New)
```python
manager.add_expense_percent_split(
    amount=300.0,
    paid_by_id="charlie",
    user_percentages={"alice": 40.0, "bob": 35.0, "charlie": 25.0},
    description="Utilities bill",
    group_id=group.group_id
)
```

#### Mixed Split (Advanced New Feature)
```python
manager.add_expense_mixed_split(
    amount=240.0,
    paid_by_id="diana",
    split_configs=[
        {"user_id": "alice", "type": "PERCENT", "percentage": 50.0},  # $120
        {"user_id": "bob", "type": "EXACT", "amount": 80.0},           # $80
        {"user_id": "diana", "type": "EQUAL"}                        # $40
    ],
    description="Restaurant dinner"
)
```

### 3. **Enhanced Balance Operations**
```python
# Group-specific balances
manager.show_user_balances("alice", group_id="group_123")

# Overall balances  
manager.show_user_balances("alice")

# Group summaries
manager.show_group_summary("group_123")

# Group-aware settlements
manager.settle_up("bob", "alice", 50.0, group_id="group_123")
```

---

## 📊 Enhanced Database Schema (5 min)

### Key Tables:
```sql
-- Enhanced Users
Users: user_id, name, email, phone, created_at, is_active

-- Groups (New)
Groups: group_id, name, description, created_by, created_at, is_active

-- Group Memberships (New)
GroupMemberships: group_id, user_id, joined_at

-- Enhanced Expenses  
Expenses: expense_id, amount, paid_by_user_id, description, 
         category, group_id, created_at

-- Enhanced Splits
ExpenseSplits: expense_id, user_id, split_type, split_value, 
              calculated_amount

-- Group-Aware Balances
Balances: from_user_id, to_user_id, amount, group_id, updated_at
```

---

## 🎯 Interview Flow (60 minutes)

### **Phase 1: Requirements** (5-8 min)
- ✅ **Functional**: Users, groups, flexible splits, balances, settlements
- ✅ **Scale**: 1M users, 10K groups, 100K expenses/day
- ✅ **Constraints**: Real-time balance updates, group context

### **Phase 2: High Level Design** (8-10 min)  
- ✅ Draw main classes with relationships
- ✅ Show User ↔ Group many-to-many relationship
- ✅ Expense → SplitDetail one-to-many
- ✅ Explain dual balance tracking (group + overall)

### **Phase 3: Detailed Design** (25-30 min)
- ✅ Start with **User** and **Group** classes
- ✅ Design **SplitDetail** dataclass for flexibility
- ✅ Implement **Expense** with mixed split calculation
- ✅ Build **BalanceManager** with group awareness
- ✅ Add **validation logic** for complex scenarios
- ✅ Show **GroupManager** for group operations

### **Phase 4: Demo & Validation** (8-10 min)
- ✅ Walk through **mixed split scenario**
- ✅ Demonstrate **group-specific balances**
- ✅ Show **settlement process** with group context
- ✅ Validate **edge cases** (percentages, exact amounts)

### **Phase 5: Extensions & Scale** (5-8 min)
- ✅ **Database design** with group tables
- ✅ **API endpoints** for all operations
- ✅ **Scaling strategies** (sharding, caching)
- ✅ **Advanced features** (recurring expenses, multi-currency)

---

## 🔧 Advanced Discussion Points

### **Complex Scenarios:**
1. **Mixed Split Validation**: How to ensure exact + percentage + equal don't exceed total?
2. **Group Member Removal**: How to handle existing balances when user leaves group?
3. **Concurrent Updates**: How to handle simultaneous expense additions in same group?

### **Scalability Questions:**
1. **10M Users**: Database sharding by user_id, read replicas for balances
2. **Real-time Updates**: WebSocket connections for live balance updates
3. **Group Optimization**: Caching for frequently accessed group data

### **Advanced Features:**
1. **Debt Simplification**: Minimize transactions using graph algorithms
2. **Recurring Expenses**: Template-based recurring group expenses
3. **Multi-Currency**: Currency conversion with exchange rates
4. **Approval Workflow**: Expense approval system for large groups

---

## ⚠️ Key Pitfalls to Avoid

1. **Don't ignore group context** - All operations should support optional group scope
2. **Don't skip mixed split validation** - Complex validation logic is crucial
3. **Don't forget dual balance tracking** - Group vs overall balances must be consistent
4. **Don't oversimplify the API** - Need multiple methods for different split types
5. **Don't ignore edge cases** - Payer must be in splits, amounts must match, etc.

---

## 💡 Key Talking Points

### **What makes this solution advanced?**
1. ✅ **Flexible Architecture** - Supports any combination of split types
2. ✅ **Group Context** - All operations work within group scope
3. ✅ **Clean APIs** - Separate methods for different use cases
4. ✅ **Robust Validation** - Comprehensive edge case handling
5. ✅ **Production Ready** - Error handling, logging, metrics

### **How does it handle complexity?**
1. ✅ **SplitDetail Pattern** - Clean data structure for individual splits
2. ✅ **Manager Separation** - Dedicated managers for different concerns
3. ✅ **Validation Layer** - Centralized validation logic
4. ✅ **Group Awareness** - Dual balance tracking system

---

## 📝 Quick Code Snippets

### Core Class Structure:
```python
@dataclass
class SplitDetail:
    user: User
    split_type: SplitType  
    value: float = 0.0
    calculated_amount: float = 0.0

class Expense:
    def __init__(self, expense_id, amount, paid_by, split_details, 
                 description="", category=ExpenseCategory.OTHER, group_id=None):
        # Calculate splits automatically
        
class BalanceManager:
    def __init__(self):
        self.overall_balances = {}      # Global balances
        self.group_balances = {}        # Group-specific balances
```

### Key Validation Logic:
```python
def validate_mixed_splits(splits, total_amount):
    exact_total = sum(s.value for s in splits if s.split_type == EXACT)
    percent_total = sum(s.value for s in splits if s.split_type == PERCENT)
    equal_count = len([s for s in splits if s.split_type == EQUAL])
    
    # Ensure exact + percentage doesn't exceed total
    # Leave remaining amount for equal splits
```

---

**Focus on: Group management, flexible APIs, robust validation, and production-ready architecture!**