# Splitwise Interview Cheat Sheet

## 📝 Quick Requirements Recap
- Users can add expenses and split them
- Support Equal, Exact, and Percentage splits
- Track who owes whom
- Settle debts between users
- Show balances

## 🗣️ Interview Flow (60 minutes)

### Phase 1: Requirements (5-8 minutes)
- Clarify functional requirements
- Discuss scale (how many users, expenses)
- Identify core entities: User, Expense, Split

### Phase 2: High Level Design (8-10 minutes)
- Draw main classes: ExpenseManager, User, Expense, Split
- Show relationships between classes
- Discuss split types hierarchy

### Phase 3: Detailed Design (25-30 minutes)
- Implement core classes with methods
- Start with User and Expense classes
- Add Split hierarchy (Abstract base + concrete)
- Implement ExpenseManager with add_expense logic
- Show balance calculation and tracking

### Phase 4: Demo & Testing (8-10 minutes)
- Walk through example scenarios
- Show equal split calculation
- Demonstrate settlement process

### Phase 5: Extensions (5-8 minutes)
- Database design
- API endpoints
- Additional features (groups, categories)
- Scaling considerations

## 🎯 Key Points to Emphasize

### Design Patterns
- **Strategy Pattern**: Different split calculations
- **Template Method**: Base Split class with validate()
- **Single Responsibility**: Each class has clear purpose

### SOLID Principles
- **S**: Each class has single responsibility
- **O**: Easy to add new split types
- **L**: All splits are interchangeable
- **I**: Clean interfaces (abstract Split)
- **D**: Manager depends on abstractions

### Code Quality
- Input validation everywhere
- Error handling with meaningful messages
- Clean method names and documentation
- Proper abstraction levels

## 🔧 Common Interview Questions & Answers

**Q: Why use abstract Split class?**
A: Allows different split calculations while maintaining same interface. Easy to add new split types (Weighted, Custom) without changing existing code.

**Q: How to handle floating point precision?**
A: Use decimal.Decimal for financial calculations, or round to 2 decimal places with proper validation.

**Q: How would you scale this system?**
A: Database for persistence, caching for balances, microservices for different domains, API gateway for client access.

**Q: What if someone adds invalid split amounts?**
A: Validate in Split.validate() method and Expense.validate(). Check totals match expense amount.

**Q: How to minimize number of transactions between users?**
A: Implement debt simplification algorithm using graph theory to find minimum spanning tree of debts.

## 🚨 Common Mistakes to Avoid

1. **Overengineering**: Don't add unnecessary complexity early
2. **No validation**: Always validate inputs (amounts, percentages)
3. **Tight coupling**: Keep classes loosely coupled
4. **Missing edge cases**: Handle self-payments, zero amounts
5. **No abstraction**: Use interfaces for extensibility
6. **Poor naming**: Use clear, descriptive names
7. **Monolithic design**: Separate concerns properly

## 📊 Time Allocation Strategy

- **Requirements & Design**: 15 minutes
- **Core Implementation**: 30 minutes  
- **Demo & Testing**: 10 minutes
- **Extensions & Discussion**: 5 minutes

## 🎪 Demo Script

```python
# 1. Create users
alice, bob, charlie = create_users()

# 2. Add equal split expense
add_dinner_expense(120, alice, [alice, bob, charlie])
show_balances()  # Bob owes Alice $40, Charlie owes Alice $40

# 3. Add exact split expense  
add_shopping_expense(100, bob, [(alice, 40), (bob, 25), (charlie, 35)])
show_balances()  # Updated balances

# 4. Settle debt
settle_payment(bob, alice, 40)
show_balances()  # Bob's debt to Alice cleared
```

## 🔍 Advanced Topics (If Time Permits)

### Database Schema
```sql
CREATE TABLE users (id, name, email);
CREATE TABLE expenses (id, amount, paid_by, description, created_at);
CREATE TABLE expense_splits (expense_id, user_id, amount);
CREATE TABLE balances (from_user, to_user, amount);
```

### API Design
```
POST /users
POST /expenses  
GET /users/{id}/balances
POST /settlements
GET /groups/{id}/expenses
```

### Scaling Strategies
- Read replicas for balance queries
- Event sourcing for audit trail
- Async processing for complex calculations
- Caching frequently accessed data

---

*Keep this handy during the interview for quick reference!*