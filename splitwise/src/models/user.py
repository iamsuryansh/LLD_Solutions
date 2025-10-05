"""
User model for Splitwise application
"""

from datetime import datetime
from typing import Set


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