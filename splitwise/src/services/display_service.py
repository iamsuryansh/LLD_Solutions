"""
Display service for Splitwise application
"""

from typing import Optional
from .balance_manager import BalanceManager
from .group_manager import GroupManager


class DisplayService:
    """Service for displaying balances and summaries"""
    
    def __init__(self, balance_manager: BalanceManager, group_manager: GroupManager, users_dict: dict):
        self.balance_manager = balance_manager
        self.group_manager = group_manager
        self.users = users_dict
    
    def show_user_balances(self, user_id: str, group_id: Optional[str] = None):
        """Show balances for a specific user"""
        user = self.users.get(user_id)
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
            other_user = self.users.get(other_user_id)
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
            debtor = self.users.get(debtor_id)
            debtor_name = debtor.name if debtor else debtor_id
            
            for creditor_id, amount in creditors.items():
                creditor = self.users.get(creditor_id)
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
            debtor = self.users.get(debtor_id)
            debtor_name = debtor.name if debtor else debtor_id
            
            for creditor_id, amount in creditors.items():
                creditor = self.users.get(creditor_id)
                creditor_name = creditor.name if creditor else creditor_id
                print(f"   • {debtor_name} owes {creditor_name}: ${amount:.2f}")
    
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