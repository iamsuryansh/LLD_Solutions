"""
SPLITWISE LOW LEVEL DESIGN - Interview Solution
==============================================

PROBLEM STATEMENT:
Design a system like Splitwise that allows users to split expenses among friends.

KEY REQUIREMENTS:
1. Users can add expenses
2. Split expenses equally or unequally among participants
3. Track who owes whom and how much
4. Settle up debts between users
5. Show balance for each user

SYSTEM FLOW:
1. Create users in the system
2. Add expenses with participants and split type
3. Calculate balances and settlements
4. Display who owes whom
5. Settle debts when payments are made

CLASSES OVERVIEW:
- User: Represents a user in the system
- Expense: Represents an expense transaction
- Split: Base class for different split types
- EqualSplit, ExactSplit, PercentSplit: Different ways to split expenses
- ExpenseManager: Main class that manages all operations
- SplitCalculator: Handles split calculations
- BalanceManager: Manages user balances and settlements

TIME COMPLEXITY: Most operations O(n) where n is number of users
SPACE COMPLEXITY: O(u + e) where u is users and e is expenses
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime

# File: models/user.py
class User:
    """Represents a user in the Splitwise system"""
    
    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        # Track how much this user owes to others
        self.balance = 0.0
        
    def __str__(self):
        return f"User({self.name}, Balance: {self.balance})"

# File: models/enums.py
class SplitType(Enum):
    """Different types of expense splitting"""
    EQUAL = "EQUAL"
    EXACT = "EXACT" 
    PERCENT = "PERCENT"

# File: models/split.py
class Split(ABC):
    """Abstract base class for different split types"""
    
    def __init__(self, user: User):
        self.user = user
        self.amount = 0.0
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate if the split is correct"""
        pass

class EqualSplit(Split):
    """Split expense equally among users"""
    
    def __init__(self, user: User):
        super().__init__(user)
    
    def validate(self) -> bool:
        return self.amount >= 0

class ExactSplit(Split):
    """Split expense with exact amounts"""
    
    def __init__(self, user: User, amount: float):
        super().__init__(user)
        self.amount = amount
    
    def validate(self) -> bool:
        return self.amount >= 0

class PercentSplit(Split):
    """Split expense by percentage"""
    
    def __init__(self, user: User, percent: float):
        super().__init__(user)
        self.percent = percent
    
    def validate(self) -> bool:
        return 0 <= self.percent <= 100

# File: models/expense.py
class Expense:
    """Represents an expense in the system"""
    
    def __init__(self, expense_id: str, amount: float, paid_by: User, 
                 splits: List[Split], description: str = ""):
        self.expense_id = expense_id
        self.amount = amount
        self.paid_by = paid_by
        self.splits = splits
        self.description = description
        self.created_at = datetime.now()
    
    def validate(self) -> bool:
        """Validate if expense is correct"""
        if self.amount <= 0:
            return False
        
        # Validate all splits
        for split in self.splits:
            if not split.validate():
                return False
        
        return True

# File: services/split_calculator.py
class SplitCalculator:
    """Handles different types of split calculations"""
    
    @staticmethod
    def calculate_equal_split(amount: float, splits: List[EqualSplit]) -> None:
        """Calculate equal split among users"""
        if not splits:
            return
        
        per_person_amount = amount / len(splits)
        for split in splits:
            split.amount = per_person_amount
    
    @staticmethod
    def calculate_exact_split(amount: float, splits: List[ExactSplit]) -> bool:
        """Validate and set exact splits"""
        total_split_amount = sum(split.amount for split in splits)
        
        # Check if total splits equal the expense amount
        if abs(total_split_amount - amount) > 0.01:  # Allow small floating point errors
            return False
        
        return True
    
    @staticmethod
    def calculate_percent_split(amount: float, splits: List[PercentSplit]) -> bool:
        """Calculate percentage splits"""
        total_percent = sum(split.percent for split in splits)
        
        # Check if percentages add up to 100
        if abs(total_percent - 100.0) > 0.01:
            return False
        
        # Calculate actual amounts
        for split in splits:
            split.amount = (split.percent / 100.0) * amount
        
        return True

# File: services/balance_manager.py
class BalanceManager:
    """Manages user balances and debt settlements"""
    
    def __init__(self):
        # Dictionary to track who owes whom: {user_id: {other_user_id: amount}}
        self.balances: Dict[str, Dict[str, float]] = {}
    
    def add_balance(self, from_user: str, to_user: str, amount: float):
        """Add balance between two users"""
        if from_user not in self.balances:
            self.balances[from_user] = {}
        
        if to_user not in self.balances[from_user]:
            self.balances[from_user][to_user] = 0.0
        
        self.balances[from_user][to_user] += amount
    
    def settle_balance(self, from_user: str, to_user: str, amount: float) -> bool:
        """Settle debt between users"""
        if (from_user not in self.balances or 
            to_user not in self.balances[from_user]):
            return False
        
        current_debt = self.balances[from_user][to_user]
        if current_debt < amount:
            return False
        
        self.balances[from_user][to_user] -= amount
        
        # Remove entry if debt is settled
        if self.balances[from_user][to_user] == 0:
            del self.balances[from_user][to_user]
            if not self.balances[from_user]:
                del self.balances[from_user]
        
        return True
    
    def get_balance_for_user(self, user_id: str) -> Dict[str, float]:
        """Get all balances for a specific user"""
        result = {}
        
        # Amount this user owes to others
        if user_id in self.balances:
            for other_user, amount in self.balances[user_id].items():
                result[other_user] = -amount  # Negative means owes
        
        # Amount others owe to this user
        for debtor, creditors in self.balances.items():
            if user_id in creditors:
                result[debtor] = creditors[user_id]  # Positive means owed
        
        return result
    
    def get_all_balances(self) -> Dict[str, Dict[str, float]]:
        """Get all balances in the system"""
        return self.balances.copy()

# File: services/expense_manager.py
class ExpenseManager:
    """Main class that manages all Splitwise operations"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.expenses: Dict[str, Expense] = {}
        self.balance_manager = BalanceManager()
        self.split_calculator = SplitCalculator()
    
    def add_user(self, user: User) -> bool:
        """Add a new user to the system"""
        if user.user_id in self.users:
            print(f"User {user.user_id} already exists")
            return False
        
        self.users[user.user_id] = user
        print(f"User {user.name} added successfully")
        return True
    
    def add_expense(self, expense: Expense) -> bool:
        """Add a new expense and update balances"""
        
        # Validate expense
        if not expense.validate():
            print("Invalid expense")
            return False
        
        # Calculate splits based on type
        if expense.splits and isinstance(expense.splits[0], EqualSplit):
            self.split_calculator.calculate_equal_split(expense.amount, expense.splits)
        
        elif expense.splits and isinstance(expense.splits[0], ExactSplit):
            if not self.split_calculator.calculate_exact_split(expense.amount, expense.splits):
                print("Exact splits don't add up to total amount")
                return False
        
        elif expense.splits and isinstance(expense.splits[0], PercentSplit):
            if not self.split_calculator.calculate_percent_split(expense.amount, expense.splits):
                print("Percentages don't add up to 100%")
                return False
        
        # Update balances
        self._update_balances(expense)
        
        # Store expense
        self.expenses[expense.expense_id] = expense
        print(f"Expense {expense.description} added successfully")
        return True
    
    def _update_balances(self, expense: Expense):
        """Update user balances after adding expense"""
        paid_by = expense.paid_by
        
        for split in expense.splits:
            if split.user.user_id != paid_by.user_id:
                # This user owes money to the person who paid
                self.balance_manager.add_balance(
                    split.user.user_id, 
                    paid_by.user_id, 
                    split.amount
                )
    
    def settle_up(self, user1_id: str, user2_id: str, amount: float) -> bool:
        """Settle debt between two users"""
        if user1_id not in self.users or user2_id not in self.users:
            print("One or both users not found")
            return False
        
        success = self.balance_manager.settle_balance(user1_id, user2_id, amount)
        if success:
            print(f"{self.users[user1_id].name} paid {amount} to {self.users[user2_id].name}")
        else:
            print("Settlement failed - insufficient debt or invalid users")
        
        return success
    
    def show_balances(self, user_id: Optional[str] = None):
        """Show balances for a specific user or all users"""
        if user_id:
            if user_id not in self.users:
                print("User not found")
                return
            
            balances = self.balance_manager.get_balance_for_user(user_id)
            user_name = self.users[user_id].name
            
            if not balances:
                print(f"{user_name} has no outstanding balances")
                return
            
            print(f"\nBalances for {user_name}:")
            for other_user_id, amount in balances.items():
                other_name = self.users[other_user_id].name
                if amount > 0:
                    print(f"  {other_name} owes you: ${amount:.2f}")
                else:
                    print(f"  You owe {other_name}: ${-amount:.2f}")
        else:
            # Show all balances
            all_balances = self.balance_manager.get_all_balances()
            if not all_balances:
                print("No outstanding balances")
                return
            
            print("\nAll Balances:")
            for debtor_id, creditors in all_balances.items():
                debtor_name = self.users[debtor_id].name
                for creditor_id, amount in creditors.items():
                    creditor_name = self.users[creditor_id].name
                    print(f"  {debtor_name} owes {creditor_name}: ${amount:.2f}")
    
    def get_user_expenses(self, user_id: str) -> List[Expense]:
        """Get all expenses involving a specific user"""
        if user_id not in self.users:
            return []
        
        user_expenses = []
        for expense in self.expenses.values():
            # Check if user paid for the expense or is part of splits
            if (expense.paid_by.user_id == user_id or 
                any(split.user.user_id == user_id for split in expense.splits)):
                user_expenses.append(expense)
        
        return user_expenses

# File: main.py - Demo Usage
def demo_splitwise():
    """Demonstration of Splitwise functionality for interview"""
    
    print("=== SPLITWISE DEMO ===\n")
    
    # Initialize the system
    expense_manager = ExpenseManager()
    
    # Create users
    alice = User("u1", "Alice", "alice@email.com")
    bob = User("u2", "Bob", "bob@email.com")
    charlie = User("u3", "Charlie", "charlie@email.com")
    
    # Add users to system
    expense_manager.add_user(alice)
    expense_manager.add_user(bob)
    expense_manager.add_user(charlie)
    
    print("\n1. EQUAL SPLIT EXAMPLE:")
    # Equal split: Dinner for $120, paid by Alice, split equally among 3 people
    equal_splits = [
        EqualSplit(alice),
        EqualSplit(bob), 
        EqualSplit(charlie)
    ]
    
    dinner_expense = Expense("e1", 120.0, alice, equal_splits, "Dinner at restaurant")
    expense_manager.add_expense(dinner_expense)
    expense_manager.show_balances()
    
    print("\n2. EXACT SPLIT EXAMPLE:")
    # Exact split: Shopping for $100, paid by Bob
    # Alice owes $40, Bob owes $25, Charlie owes $35
    exact_splits = [
        ExactSplit(alice, 40.0),
        ExactSplit(bob, 25.0),
        ExactSplit(charlie, 35.0)
    ]
    
    shopping_expense = Expense("e2", 100.0, bob, exact_splits, "Grocery shopping")
    expense_manager.add_expense(shopping_expense)
    expense_manager.show_balances()
    
    print("\n3. SETTLEMENT EXAMPLE:")
    # Bob pays Alice $40
    expense_manager.settle_up("u2", "u1", 40.0)
    expense_manager.show_balances()
    
    print("\n4. USER-SPECIFIC BALANCES:")
    expense_manager.show_balances("u1")  # Alice's balances
    expense_manager.show_balances("u2")  # Bob's balances

if __name__ == "__main__":
    demo_splitwise()