"""
Group manager service for Splitwise application
"""

import uuid
from typing import Dict, List, Optional
from ..models import Group, User


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