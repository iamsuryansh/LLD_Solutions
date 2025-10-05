"""
Split validator for Splitwise application
"""

from typing import List, Tuple
from ..enums import SplitType
from ..models import SplitDetail


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