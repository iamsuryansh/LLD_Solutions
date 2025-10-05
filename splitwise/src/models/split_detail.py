"""
Split detail model for Splitwise application
"""

from dataclasses import dataclass
from ..enums import SplitType
from .user import User


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