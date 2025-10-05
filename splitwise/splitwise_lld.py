"""
SPLITWISE LOW LEVEL DESIGN - Enhanced User & Group-Centric Solution
==================================================================

PROBLEM STATEMENT:
Design a comprehensive expense-sharing system like Splitwise with advanced user and group management.

KEY REQUIREMENTS:
1. User Management: Add/remove users, user profiles
2. Group Management: Create groups, add/remove users from groups
3. Flexible Expense Splitting: Pass list of users with various split parameters
4. Multiple Split Types: Equal, Exact, Percentage splits within same expense
5. Advanced Balance Tracking: Group-wise and overall balances
6. Settlement System: Settle debts between users
7. Group Activities: Track group expenses and settlements

SYSTEM FLOW:
1. Register users in the system
2. Create groups and manage memberships
3. Add expenses to groups with flexible participant selection
4. Calculate splits using various strategies (equal, exact, percentage)
5. Track balances at user and group levels
6. Settle debts with proper validation
7. Generate reports and balance summaries

CLASSES OVERVIEW:
- User: Enhanced user with profile and group memberships
- Group: Manages group of users and group-specific expenses
- Expense: Enhanced expense with flexible participant handling
- SplitDetail: Individual split configuration for each user
- SplitValidator: Validates split configurations
- ExpenseManager: Main orchestrator with group support
- BalanceManager: Advanced balance tracking with group context
- GroupManager: Dedicated group operations management

TIME COMPLEXITY: Most operations O(n) where n is number of participants
SPACE COMPLEXITY: O(u + g + e) where u=users, g=groups, e=expenses
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Set, Union, Tuple
from datetime import datetime
import uuid
from dataclasses import dataclass

# ================================
# Core Models and Enums
# ================================

class User:
    """Enhanced user model with group membership and profile management"""
    
    def __init__(self, user_id: str, name: str, email: str, phone: str = ""):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.created_at = datetime.now()
        self.group_memberships: Set[str] = set()  # Set of group IDs
        self.is_active = True
        
    def add_to_group(self, group_id: str) -> None:
        """Add user to a group"""
        self.group_memberships.add(group_id)
    
    def remove_from_group(self, group_id: str) -> None:
        """Remove user from a group"""
        self.group_memberships.discard(group_id)
    
    def is_member_of_group(self, group_id: str) -> bool:
        """Check if user is member of a group"""
        return group_id in self.group_memberships
        
    def __str__(self):
        return f"User({self.name}, Groups: {len(self.group_memberships)})"
    
    def __eq__(self, other):
        return isinstance(other, User) and self.user_id == other.user_id
    
    def __hash__(self):
        return hash(self.user_id)

class Group:
    """Represents a group of users who share expenses"""
    
    def __init__(self, group_id: str, name: str, description: str = "", created_by: str = ""):
        self.group_id = group_id
        self.name = name
        self.description = description
        self.created_by = created_by  # User ID of creator
        self.created_at = datetime.now()
        self.members: Dict[str, User] = {}  # user_id -> User
        self.expenses: List[str] = []  # List of expense IDs
        self.is_active = True
    
    def add_member(self, user: User) -> bool:
        """Add a user to the group"""
        if user.user_id in self.members:
            return False
        
        self.members[user.user_id] = user
        user.add_to_group(self.group_id)
        return True
    
    def remove_member(self, user_id: str) -> bool:
        """Remove a user from the group"""
        if user_id not in self.members:
            return False
        
        user = self.members[user_id]
        user.remove_from_group(self.group_id)
        del self.members[user_id]
        return True
    
    def get_member_ids(self) -> List[str]:
        """Get list of member user IDs"""
        return list(self.members.keys())
    
    def get_members(self) -> List[User]:
        """Get list of member User objects"""
        return list(self.members.values())
    
    def is_member(self, user_id: str) -> bool:
        """Check if user is a member of this group"""
        return user_id in self.members
    
    def add_expense(self, expense_id: str) -> None:
        """Add an expense to this group"""
        self.expenses.append(expense_id)
    
    def __str__(self):
        return f"Group({self.name}, Members: {len(self.members)}, Expenses: {len(self.expenses)})"

class SplitType(Enum):
    """Different types of expense splitting"""
    EQUAL = "EQUAL"
    EXACT = "EXACT" 
    PERCENT = "PERCENT"

class ExpenseCategory(Enum):
    """Categories for expenses"""
    FOOD = "FOOD"
    TRAVEL = "TRAVEL"
    ENTERTAINMENT = "ENTERTAINMENT"
    UTILITIES = "UTILITIES"
    SHOPPING = "SHOPPING"
    OTHER = "OTHER"

@dataclass
class SplitDetail:
    """Details for how to split an expense for a specific user"""
    user: User
    split_type: SplitType
    value: float = 0.0  # Amount for EXACT, percentage for PERCENT, ignored for EQUAL
    calculated_amount: float = 0.0  # Final calculated amount
    
    def __post_init__(self):
        if self.split_type == SplitType.EXACT:
            self.calculated_amount = self.value

# ================================
# Split System
# ================================

class SplitValidator:
    """Validates split configurations"""
    
    @staticmethod
    def validate_splits(splits: List[SplitDetail], total_amount: float) -> Tuple[bool, str]:
        """Validate if splits are correct for the given amount"""
        if not splits:
            return False, "No splits provided"
        
        # Group splits by type for validation
        equal_splits = [s for s in splits if s.split_type == SplitType.EQUAL]
        exact_splits = [s for s in splits if s.split_type == SplitType.EXACT]
        percent_splits = [s for s in splits if s.split_type == SplitType.PERCENT]
        
        # Validate exact splits
        if exact_splits:
            total_exact = sum(s.value for s in exact_splits)
            if total_exact < 0:
                return False, "Exact amounts cannot be negative"
        
        # Validate percent splits
        if percent_splits:
            total_percent = sum(s.value for s in percent_splits)
            if total_percent < 0 or total_percent > 100:
                return False, "Percentages must be between 0 and 100"
        
        # If we have a mix, validate that they don't exceed total
        if exact_splits and percent_splits:
            exact_total = sum(s.value for s in exact_splits)
            percent_total = sum(s.value for s in percent_splits)
            percent_amount = (percent_total / 100.0) * total_amount
            
            if exact_total + percent_amount > total_amount + 0.01:  # Allow small floating point errors
                return False, "Exact amounts and percentages exceed total amount"
        
        return True, "Valid splits"

class Expense:
    """Enhanced expense model with flexible split handling"""
    
    def __init__(self, expense_id: str, amount: float, paid_by: User, 
                 split_details: List[SplitDetail], description: str = "",
                 category: ExpenseCategory = ExpenseCategory.OTHER, 
                 group_id: Optional[str] = None):
        self.expense_id = expense_id
        self.amount = amount
        self.paid_by = paid_by
        self.split_details = split_details
        self.description = description
        self.category = category
        self.group_id = group_id
        self.created_at = datetime.now()
        self.is_settled = False
        
        # Validate and calculate splits
        self._calculate_splits()
    
    def _calculate_splits(self) -> None:
        """Calculate final amounts for each split"""
        # Group splits by type
        equal_splits = [s for s in self.split_details if s.split_type == SplitType.EQUAL]
        exact_splits = [s for s in self.split_details if s.split_type == SplitType.EXACT]
        percent_splits = [s for s in self.split_details if s.split_type == SplitType.PERCENT]
        
        # Calculate amounts already accounted for
        exact_total = sum(s.value for s in exact_splits)
        percent_amount = sum((s.value / 100.0) * self.amount for s in percent_splits)
        
        # Set calculated amounts for exact and percent splits
        for split in exact_splits:
            split.calculated_amount = split.value
        
        for split in percent_splits:
            split.calculated_amount = (split.value / 100.0) * self.amount
        
        # Calculate equal split amount (remaining amount divided equally)
        if equal_splits:
            remaining_amount = self.amount - exact_total - percent_amount
            equal_amount = remaining_amount / len(equal_splits)
            
            for split in equal_splits:
                split.calculated_amount = equal_amount
    
    def get_participant_user_ids(self) -> List[str]:
        """Get list of all participant user IDs"""
        return [split.user.user_id for split in self.split_details]
    
    def get_split_for_user(self, user_id: str) -> Optional[SplitDetail]:
        """Get split detail for a specific user"""
        for split in self.split_details:
            if split.user.user_id == user_id:
                return split
        return None
    
    def validate(self) -> Tuple[bool, str]:
        """Validate if expense is correct"""
        if self.amount <= 0:
            return False, "Amount must be positive"
        
        if not self.split_details:
            return False, "No split details provided"
        
        # Check if paid_by user is included in splits
        payer_in_splits = any(split.user.user_id == self.paid_by.user_id for split in self.split_details)
        if not payer_in_splits:
            return False, "Payer must be included in the splits"
        
        # Validate splits using validator
        return SplitValidator.validate_splits(self.split_details, self.amount)
    
    def get_total_calculated_amount(self) -> float:
        """Get sum of all calculated split amounts"""
        return sum(split.calculated_amount for split in self.split_details)
    
    def __str__(self):
        return f"Expense({self.description}: ${self.amount}, Participants: {len(self.split_details)})"

# ================================
# Balance Management System
# ================================

class BalanceManager:
    """Enhanced balance manager with group support"""
    
    def __init__(self):
        # Overall balances: {user_id: {other_user_id: amount}}
        self.overall_balances: Dict[str, Dict[str, float]] = {}
        # Group-specific balances: {group_id: {user_id: {other_user_id: amount}}}
        self.group_balances: Dict[str, Dict[str, Dict[str, float]]] = {}
    
    def add_balance(self, from_user: str, to_user: str, amount: float, group_id: Optional[str] = None):
        """Add balance between two users, optionally within a group context"""
        if amount <= 0:
            return
            
        # Update overall balances
        if from_user not in self.overall_balances:
            self.overall_balances[from_user] = {}
        
        if to_user not in self.overall_balances[from_user]:
            self.overall_balances[from_user][to_user] = 0.0
        
        self.overall_balances[from_user][to_user] += amount
        
        # Update group-specific balances if group_id provided
        if group_id:
            if group_id not in self.group_balances:
                self.group_balances[group_id] = {}
            
            if from_user not in self.group_balances[group_id]:
                self.group_balances[group_id][from_user] = {}
            
            if to_user not in self.group_balances[group_id][from_user]:
                self.group_balances[group_id][from_user][to_user] = 0.0
            
            self.group_balances[group_id][from_user][to_user] += amount
    
    def settle_balance(self, from_user: str, to_user: str, amount: float, group_id: Optional[str] = None) -> bool:
        """Settle debt between users"""
        # Check overall balance
        if (from_user not in self.overall_balances or 
            to_user not in self.overall_balances[from_user]):
            return False
        
        current_debt = self.overall_balances[from_user][to_user]
        if current_debt < amount:
            return False
        
        # Update overall balance
        self.overall_balances[from_user][to_user] -= amount
        
        # Clean up if debt is settled
        if abs(self.overall_balances[from_user][to_user]) < 0.01:
            del self.overall_balances[from_user][to_user]
            if not self.overall_balances[from_user]:
                del self.overall_balances[from_user]
        
        # Update group balance if specified
        if group_id and group_id in self.group_balances:
            if (from_user in self.group_balances[group_id] and 
                to_user in self.group_balances[group_id][from_user]):
                
                self.group_balances[group_id][from_user][to_user] -= amount
                
                # Clean up group balance
                if abs(self.group_balances[group_id][from_user][to_user]) < 0.01:
                    del self.group_balances[group_id][from_user][to_user]
                    if not self.group_balances[group_id][from_user]:
                        del self.group_balances[group_id][from_user]
        
        return True
    
    def get_balance_for_user(self, user_id: str, group_id: Optional[str] = None) -> Dict[str, float]:
        """Get balances for a specific user, optionally within a group"""
        result = {}
        balances_to_check = self.overall_balances
        
        if group_id and group_id in self.group_balances:
            balances_to_check = self.group_balances[group_id]
        
        # Amount this user owes to others
        if user_id in balances_to_check:
            for other_user, amount in balances_to_check[user_id].items():
                result[other_user] = -amount  # Negative means owes
        
        # Amount others owe to this user
        for debtor, creditors in balances_to_check.items():
            if user_id in creditors:
                if debtor not in result:
                    result[debtor] = 0.0
                result[debtor] += creditors[user_id]  # Positive means owed
        
        return result
    
    def get_group_balances(self, group_id: str) -> Dict[str, Dict[str, float]]:
        """Get all balances within a specific group"""
        if group_id not in self.group_balances:
            return {}
        return self.group_balances[group_id].copy()
    
    def get_all_balances(self) -> Dict[str, Dict[str, float]]:
        """Get all overall balances in the system"""
        return self.overall_balances.copy()
    
    def get_user_net_balance(self, user_id: str, group_id: Optional[str] = None) -> float:
        """Calculate net balance for a user (positive = owed money, negative = owes money)"""
        user_balances = self.get_balance_for_user(user_id, group_id)
        return sum(user_balances.values())

# ================================
# Group Management System
# ================================

class GroupManager:
    """Manages group operations and memberships"""
    
    def __init__(self):
        self.groups: Dict[str, Group] = {}
    
    def create_group(self, name: str, description: str = "", created_by: str = "") -> Group:
        """Create a new group"""
        group_id = f"group_{uuid.uuid4().hex[:8]}"
        group = Group(group_id, name, description, created_by)
        self.groups[group_id] = group
        return group
    
    def get_group(self, group_id: str) -> Optional[Group]:
        """Get a group by ID"""
        return self.groups.get(group_id)
    
    def add_user_to_group(self, group_id: str, user: User) -> bool:
        """Add user to a group"""
        if group_id not in self.groups:
            return False
        
        return self.groups[group_id].add_member(user)
    
    def remove_user_from_group(self, group_id: str, user_id: str) -> bool:
        """Remove user from a group"""
        if group_id not in self.groups:
            return False
        
        return self.groups[group_id].remove_member(user_id)
    
    def get_user_groups(self, user_id: str) -> List[Group]:
        """Get all groups a user belongs to"""
        user_groups = []
        for group in self.groups.values():
            if group.is_member(user_id):
                user_groups.append(group)
        return user_groups
    
    def deactivate_group(self, group_id: str) -> bool:
        """Deactivate a group (soft delete)"""
        if group_id not in self.groups:
            return False
        
        self.groups[group_id].is_active = False
        return True

# ================================
# Main Expense Management System
# ================================

class ExpenseManager:
    """Enhanced expense manager with group support and flexible splitting"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.expenses: Dict[str, Expense] = {}
        self.balance_manager = BalanceManager()
        self.group_manager = GroupManager()
    
    # ================================
    # User Management
    # ================================
    
    def add_user(self, user_id: str, name: str, email: str, phone: str = "") -> User:
        """Add a new user to the system"""
        if user_id in self.users:
            raise ValueError(f"User {user_id} already exists")
        
        user = User(user_id, name, email, phone)
        self.users[user_id] = user
        print(f"✅ User {name} added successfully")
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        return self.users.get(user_id)
    
    def get_users_by_ids(self, user_ids: List[str]) -> List[User]:
        """Get multiple users by their IDs"""
        users = []
        for user_id in user_ids:
            user = self.get_user(user_id)
            if user:
                users.append(user)
        return users
    
    # ================================
    # Group Management
    # ================================
    
    def create_group(self, name: str, description: str = "", created_by: str = "") -> Group:
        """Create a new group"""
        group = self.group_manager.create_group(name, description, created_by)
        print(f"✅ Group '{name}' created with ID: {group.group_id}")
        return group
    
    def add_users_to_group(self, group_id: str, user_ids: List[str]) -> bool:
        """Add multiple users to a group"""
        group = self.group_manager.get_group(group_id)
        if not group:
            print(f"❌ Group {group_id} not found")
            return False
        
        added_count = 0
        for user_id in user_ids:
            user = self.get_user(user_id)
            if user and group.add_member(user):
                added_count += 1
        
        print(f"✅ Added {added_count} users to group '{group.name}'")
        return added_count > 0
    
    def get_group(self, group_id: str) -> Optional[Group]:
        """Get a group by ID"""
        return self.group_manager.get_group(group_id)
    
    # ================================
    # Expense Management with Flexible Splitting
    # ================================
    
    def add_expense_equal_split(self, amount: float, paid_by_id: str, participant_ids: List[str],
                               description: str = "", category: ExpenseCategory = ExpenseCategory.OTHER,
                               group_id: Optional[str] = None) -> Optional[Expense]:
        """Add expense with equal split among participants"""
        
        # Get users
        paid_by = self.get_user(paid_by_id)
        participants = self.get_users_by_ids(participant_ids)
        
        if not paid_by:
            print(f"❌ Payer {paid_by_id} not found")
            return None
        
        if len(participants) != len(participant_ids):
            print(f"❌ Some participant users not found")
            return None
        
        # Create equal split details
        split_details = [SplitDetail(user=user, split_type=SplitType.EQUAL) for user in participants]
        
        return self._create_expense(amount, paid_by, split_details, description, category, group_id)
    
    def add_expense_exact_split(self, amount: float, paid_by_id: str, 
                               user_amounts: Dict[str, float], description: str = "",
                               category: ExpenseCategory = ExpenseCategory.OTHER,
                               group_id: Optional[str] = None) -> Optional[Expense]:
        """Add expense with exact amounts for each user"""
        
        # Get payer
        paid_by = self.get_user(paid_by_id)
        if not paid_by:
            print(f"❌ Payer {paid_by_id} not found")
            return None
        
        # Create exact split details
        split_details = []
        for user_id, user_amount in user_amounts.items():
            user = self.get_user(user_id)
            if not user:
                print(f"❌ User {user_id} not found")
                return None
            split_details.append(SplitDetail(user=user, split_type=SplitType.EXACT, value=user_amount))
        
        return self._create_expense(amount, paid_by, split_details, description, category, group_id)
    
    def add_expense_percent_split(self, amount: float, paid_by_id: str,
                                 user_percentages: Dict[str, float], description: str = "",
                                 category: ExpenseCategory = ExpenseCategory.OTHER,
                                 group_id: Optional[str] = None) -> Optional[Expense]:
        """Add expense with percentage splits for each user"""
        
        # Validate percentages add up to 100
        if abs(sum(user_percentages.values()) - 100.0) > 0.01:
            print(f"❌ Percentages must add up to 100, got {sum(user_percentages.values())}")
            return None
        
        # Get payer
        paid_by = self.get_user(paid_by_id)
        if not paid_by:
            print(f"❌ Payer {paid_by_id} not found")
            return None
        
        # Create percent split details
        split_details = []
        for user_id, percentage in user_percentages.items():
            user = self.get_user(user_id)
            if not user:
                print(f"❌ User {user_id} not found")
                return None
            split_details.append(SplitDetail(user=user, split_type=SplitType.PERCENT, value=percentage))
        
        return self._create_expense(amount, paid_by, split_details, description, category, group_id)
    
    def add_expense_mixed_split(self, amount: float, paid_by_id: str,
                               split_configs: List[Dict[str, any]], description: str = "",
                               category: ExpenseCategory = ExpenseCategory.OTHER,
                               group_id: Optional[str] = None) -> Optional[Expense]:
        """Add expense with mixed split types
        
        split_configs format:
        [
            {"user_id": "u1", "type": "EQUAL"},
            {"user_id": "u2", "type": "EXACT", "amount": 50.0},
            {"user_id": "u3", "type": "PERCENT", "percentage": 30.0}
        ]
        """
        
        # Get payer
        paid_by = self.get_user(paid_by_id)
        if not paid_by:
            print(f"❌ Payer {paid_by_id} not found")
            return None
        
        # Create mixed split details
        split_details = []
        for config in split_configs:
            user_id = config.get("user_id")
            split_type_str = config.get("type", "EQUAL")
            
            user = self.get_user(user_id)
            if not user:
                print(f"❌ User {user_id} not found")
                return None
            
            try:
                split_type = SplitType(split_type_str)
            except ValueError:
                print(f"❌ Invalid split type: {split_type_str}")
                return None
            
            if split_type == SplitType.EQUAL:
                split_details.append(SplitDetail(user=user, split_type=SplitType.EQUAL))
            elif split_type == SplitType.EXACT:
                amount_val = config.get("amount", 0.0)
                split_details.append(SplitDetail(user=user, split_type=SplitType.EXACT, value=amount_val))
            elif split_type == SplitType.PERCENT:
                percentage = config.get("percentage", 0.0)
                split_details.append(SplitDetail(user=user, split_type=SplitType.PERCENT, value=percentage))
        
        return self._create_expense(amount, paid_by, split_details, description, category, group_id)
    
    def _create_expense(self, amount: float, paid_by: User, split_details: List[SplitDetail],
                       description: str, category: ExpenseCategory, group_id: Optional[str]) -> Optional[Expense]:
        """Internal method to create and validate expense"""
        
        expense_id = f"exp_{uuid.uuid4().hex[:8]}"
        expense = Expense(expense_id, amount, paid_by, split_details, description, category, group_id)
        
        # Validate expense
        is_valid, error_msg = expense.validate()
        if not is_valid:
            print(f"❌ Invalid expense: {error_msg}")
            return None
        
        # Validate total amount matches (for mixed splits)
        total_calculated = expense.get_total_calculated_amount()
        if abs(total_calculated - amount) > 0.01:
            print(f"❌ Split amounts ({total_calculated}) don't match expense amount ({amount})")
            return None
        
        # Update balances
        self._update_balances(expense)
        
        # Store expense
        self.expenses[expense_id] = expense
        
        # Add to group if specified
        if group_id:
            group = self.group_manager.get_group(group_id)
            if group:
                group.add_expense(expense_id)
        
        print(f"✅ Expense '{description}' (${amount}) added successfully")
        self._print_expense_summary(expense)
        
        return expense
    
    def _update_balances(self, expense: Expense):
        """Update user balances after adding expense"""
        paid_by = expense.paid_by
        
        for split in expense.split_details:
            if split.user.user_id != paid_by.user_id:
                # This user owes money to the person who paid
                self.balance_manager.add_balance(
                    split.user.user_id, 
                    paid_by.user_id, 
                    split.calculated_amount,
                    expense.group_id
                )
    
    def _print_expense_summary(self, expense: Expense):
        """Print a summary of the expense and splits"""
        print(f"   Paid by: {expense.paid_by.name}")
        print(f"   Split details:")
        for split in expense.split_details:
            print(f"     • {split.user.name}: ${split.calculated_amount:.2f} ({split.split_type.value})")
    
    # ================================
    # Settlement System
    # ================================
    
    def settle_up(self, from_user_id: str, to_user_id: str, amount: float, group_id: Optional[str] = None) -> bool:
        """Settle debt between two users"""
        from_user = self.get_user(from_user_id)
        to_user = self.get_user(to_user_id)
        
        if not from_user or not to_user:
            print("❌ One or both users not found")
            return False
        
        success = self.balance_manager.settle_balance(from_user_id, to_user_id, amount, group_id)
        if success:
            context = f" in group {group_id}" if group_id else ""
            print(f"✅ {from_user.name} paid ${amount} to {to_user.name}{context}")
        else:
            print("❌ Settlement failed - insufficient debt or invalid users")
        
        return success
    
    # ================================
    # Balance and Reporting System
    # ================================
    
    def show_user_balances(self, user_id: str, group_id: Optional[str] = None):
        """Show balances for a specific user"""
        user = self.get_user(user_id)
        if not user:
            print("❌ User not found")
            return
        
        balances = self.balance_manager.get_balance_for_user(user_id, group_id)
        context = f" in group {group_id}" if group_id else ""
        
        if not balances:
            print(f"✅ {user.name} has no outstanding balances{context}")
            return
        
        print(f"\n💰 Balances for {user.name}{context}:")
        net_balance = 0.0
        
        for other_user_id, amount in balances.items():
            other_user = self.get_user(other_user_id)
            other_name = other_user.name if other_user else other_user_id
            
            if amount > 0:
                print(f"   ✅ {other_name} owes you: ${amount:.2f}")
            else:
                print(f"   ❌ You owe {other_name}: ${-amount:.2f}")
            
            net_balance += amount
        
        if net_balance > 0:
            print(f"   📊 Net: You are owed ${net_balance:.2f}")
        elif net_balance < 0:
            print(f"   📊 Net: You owe ${-net_balance:.2f}")
        else:
            print(f"   📊 Net: Balanced")
    
    def show_group_balances(self, group_id: str):
        """Show all balances within a group"""
        group = self.group_manager.get_group(group_id)
        if not group:
            print("❌ Group not found")
            return
        
        group_balances = self.balance_manager.get_group_balances(group_id)
        
        if not group_balances:
            print(f"✅ No outstanding balances in group '{group.name}'")
            return
        
        print(f"\n💰 Balances in group '{group.name}':")
        for debtor_id, creditors in group_balances.items():
            debtor = self.get_user(debtor_id)
            debtor_name = debtor.name if debtor else debtor_id
            
            for creditor_id, amount in creditors.items():
                creditor = self.get_user(creditor_id)
                creditor_name = creditor.name if creditor else creditor_id
                print(f"   • {debtor_name} owes {creditor_name}: ${amount:.2f}")
    
    def show_all_balances(self):
        """Show all balances in the system"""
        all_balances = self.balance_manager.get_all_balances()
        
        if not all_balances:
            print("✅ No outstanding balances in the system")
            return
        
        print(f"\n💰 All System Balances:")
        for debtor_id, creditors in all_balances.items():
            debtor = self.get_user(debtor_id)
            debtor_name = debtor.name if debtor else debtor_id
            
            for creditor_id, amount in creditors.items():
                creditor = self.get_user(creditor_id)
                creditor_name = creditor.name if creditor else creditor_id
                print(f"   • {debtor_name} owes {creditor_name}: ${amount:.2f}")
    
    def get_user_expenses(self, user_id: str, group_id: Optional[str] = None) -> List[Expense]:
        """Get all expenses involving a specific user"""
        if user_id not in self.users:
            return []
        
        user_expenses = []
        for expense in self.expenses.values():
            # Filter by group if specified
            if group_id and expense.group_id != group_id:
                continue
            
            # Check if user paid for the expense or is part of splits
            if (expense.paid_by.user_id == user_id or 
                any(split.user.user_id == user_id for split in expense.split_details)):
                user_expenses.append(expense)
        
        return user_expenses
    
    def show_group_summary(self, group_id: str):
        """Show comprehensive group summary"""
        group = self.group_manager.get_group(group_id)
        if not group:
            print("❌ Group not found")
            return
        
        print(f"\n📊 Group Summary: '{group.name}'")
        print(f"   Created: {group.created_at.strftime('%Y-%m-%d')}")
        print(f"   Members: {len(group.members)}")
        print(f"   Expenses: {len(group.expenses)}")
        
        # Show members
        print(f"\n👥 Members:")
        for member in group.get_members():
            net_balance = self.balance_manager.get_user_net_balance(member.user_id, group_id)
            status = "owes money" if net_balance < 0 else "owed money" if net_balance > 0 else "balanced"
            print(f"   • {member.name} ({status})")
        
        # Show balances
        self.show_group_balances(group_id)

# ================================
# Demo and Testing
# ================================

def demo_enhanced_splitwise():
    """Comprehensive demonstration of enhanced Splitwise functionality"""
    
    print("🚀 ENHANCED SPLITWISE DEMO - User & Group-Centric")
    print("=" * 60)
    
    # Initialize the system
    expense_manager = ExpenseManager()
    
    print("\n1️⃣ CREATING USERS")
    print("-" * 30)
    
    # Create users
    alice = expense_manager.add_user("alice", "Alice Johnson", "alice@email.com", "555-0101")
    bob = expense_manager.add_user("bob", "Bob Smith", "bob@email.com", "555-0102")
    charlie = expense_manager.add_user("charlie", "Charlie Brown", "charlie@email.com", "555-0103")
    diana = expense_manager.add_user("diana", "Diana Wilson", "diana@email.com", "555-0104")
    
    print("\n2️⃣ CREATING GROUPS")
    print("-" * 30)
    
    # Create groups
    roommates_group = expense_manager.create_group("Roommates", "Shared apartment expenses", "alice")
    vacation_group = expense_manager.create_group("Beach Vacation", "Summer 2024 trip", "bob")
    
    # Add users to groups
    expense_manager.add_users_to_group(roommates_group.group_id, ["alice", "bob", "charlie"])
    expense_manager.add_users_to_group(vacation_group.group_id, ["alice", "bob", "diana"])
    
    print("\n3️⃣ ADDING EXPENSES - EQUAL SPLITS")
    print("-" * 40)
    
    # Equal split examples
    expense_manager.add_expense_equal_split(
        amount=150.0,
        paid_by_id="alice",
        participant_ids=["alice", "bob", "charlie"],
        description="Grocery shopping",
        category=ExpenseCategory.FOOD,
        group_id=roommates_group.group_id
    )
    
    print("\n4️⃣ ADDING EXPENSES - EXACT SPLITS")
    print("-" * 40)
    
    # Exact split example
    expense_manager.add_expense_exact_split(
        amount=200.0,
        paid_by_id="bob",
        user_amounts={"alice": 80.0, "bob": 60.0, "diana": 60.0},
        description="Hotel booking",
        category=ExpenseCategory.TRAVEL,
        group_id=vacation_group.group_id
    )
    
    print("\n5️⃣ ADDING EXPENSES - PERCENTAGE SPLITS")
    print("-" * 45)
    
    # Percentage split example
    expense_manager.add_expense_percent_split(
        amount=300.0,
        paid_by_id="charlie",
        user_percentages={"alice": 40.0, "bob": 35.0, "charlie": 25.0},
        description="Utilities bill",
        category=ExpenseCategory.UTILITIES,
        group_id=roommates_group.group_id
    )
    
    print("\n6️⃣ ADDING EXPENSES - MIXED SPLITS")
    print("-" * 40)
    
    # Mixed split example
    expense_manager.add_expense_mixed_split(
        amount=240.0,
        paid_by_id="diana",
        split_configs=[
            {"user_id": "alice", "type": "PERCENT", "percentage": 50.0},  # $120
            {"user_id": "bob", "type": "EXACT", "amount": 80.0},           # $80
            {"user_id": "diana", "type": "EQUAL"}                        # $40 (remaining)
        ],
        description="Restaurant dinner",
        category=ExpenseCategory.FOOD,
        group_id=vacation_group.group_id
    )
    
    print("\n7️⃣ BALANCE SUMMARIES")
    print("-" * 30)
    
    # Show individual balances
    expense_manager.show_user_balances("alice")
    expense_manager.show_user_balances("bob")
    
    # Show group balances
    expense_manager.show_group_balances(roommates_group.group_id)
    expense_manager.show_group_balances(vacation_group.group_id)
    
    print("\n8️⃣ SETTLEMENTS")
    print("-" * 20)
    
    # Settle some debts
    expense_manager.settle_up("bob", "alice", 50.0, roommates_group.group_id)
    expense_manager.settle_up("charlie", "alice", 75.0)
    
    # Show updated balances
    print("\n📊 UPDATED BALANCES AFTER SETTLEMENTS:")
    expense_manager.show_user_balances("alice")
    expense_manager.show_user_balances("bob")
    expense_manager.show_user_balances("charlie")
    
    print("\n9️⃣ GROUP SUMMARIES")
    print("-" * 30)
    
    # Show comprehensive group summaries
    expense_manager.show_group_summary(roommates_group.group_id)
    expense_manager.show_group_summary(vacation_group.group_id)
    
    print("\n🔟 SYSTEM OVERVIEW")
    print("-" * 25)
    
    expense_manager.show_all_balances()
    
    print(f"\n✅ Demo completed successfully!")
    print(f"📈 Total users: {len(expense_manager.users)}")
    print(f"👥 Total groups: {len(expense_manager.group_manager.groups)}")
    print(f"💳 Total expenses: {len(expense_manager.expenses)}")
    
    return expense_manager

if __name__ == "__main__":
    # Run the comprehensive demo
    manager = demo_enhanced_splitwise()
    
    print(f"\n" + "=" * 60)
    print("🎯 KEY ENHANCEMENTS DEMONSTRATED:")
    print("1. ✅ User management with profiles and group memberships")
    print("2. ✅ Group creation and membership management") 
    print("3. ✅ Flexible expense splitting (equal, exact, percentage, mixed)")
    print("4. ✅ Group-specific and overall balance tracking")
    print("5. ✅ Advanced settlement system with group context")
    print("6. ✅ Comprehensive reporting and balance summaries")
    print("7. ✅ Category-based expense organization")
    print("8. ✅ Robust validation and error handling")