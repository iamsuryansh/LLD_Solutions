"""
Group model for Splitwise application
"""

from datetime import datetime
from typing import Dict, List
from .user import User


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