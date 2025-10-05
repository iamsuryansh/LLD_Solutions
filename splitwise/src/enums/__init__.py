"""
Enums and constants for Splitwise application
"""

from enum import Enum


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