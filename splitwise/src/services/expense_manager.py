"""
Expense manager service for Splitwise application
"""

import uuid
from typing import Dict, List, Optional, Any
from ..enums import ExpenseCategory, SplitType
from ..models import User, Expense, SplitDetail
from ..validators import SplitValidator
from .balance_manager import BalanceManager
from .group_manager import GroupManager


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
    
    def create_group(self, name: str, description: str = "", created_by: str = ""):
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
    
    def get_group(self, group_id: str):
        """Get a group by ID"""
        return self.group_manager.get_group(group_id)
    
    # ================================
    # Expense Management
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
                               split_configs: List[Dict[str, Any]], description: str = "",
                               category: ExpenseCategory = ExpenseCategory.OTHER,
                               group_id: Optional[str] = None) -> Optional[Expense]:
        """Add expense with mixed split types"""
        
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
        
        # Validate splits
        is_valid_splits, split_error = SplitValidator.validate_splits(split_details, amount)
        if not is_valid_splits:
            print(f"❌ Invalid splits: {split_error}")
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