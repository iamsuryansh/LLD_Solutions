"""
Expense model for Splitwise application
"""

from datetime import datetime
from typing import List, Optional, Tuple
from ..enums import ExpenseCategory, SplitType
from .user import User
from .split_detail import SplitDetail


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
        
        return True, "Valid expense"
    
    def get_total_calculated_amount(self) -> float:
        """Get sum of all calculated split amounts"""
        return sum(split.calculated_amount for split in self.split_details)
    
    def __str__(self):
        return f"Expense({self.description}: ${self.amount}, Participants: {len(self.split_details)})"