"""
Balance manager service for Splitwise application
"""

from typing import Dict, Optional


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