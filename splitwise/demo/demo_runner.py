"""
Demo runner for Splitwise application
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import ExpenseManager, ExpenseCategory, DisplayService


class SplitWiseDemo:
    """Comprehensive demonstration of Splitwise functionality"""
    
    def __init__(self):
        self.expense_manager = ExpenseManager()
        self.display_service = DisplayService(
            self.expense_manager.balance_manager,
            self.expense_manager.group_manager, 
            self.expense_manager.users
        )
    
    def run_demo(self):
        """Run the comprehensive demo"""
        
        print("🚀 ENHANCED SPLITWISE DEMO - User & Group-Centric")
        print("=" * 60)
        
        self._create_users()
        self._create_groups()
        self._add_expenses()
        self._show_balances()
        self._perform_settlements()
        self._show_summaries()
        
        print(f"\n✅ Demo completed successfully!")
        print(f"📈 Total users: {len(self.expense_manager.users)}")
        print(f"👥 Total groups: {len(self.expense_manager.group_manager.groups)}")
        print(f"💳 Total expenses: {len(self.expense_manager.expenses)}")
    
    def _create_users(self):
        """Create demo users"""
        print("\n1️⃣ CREATING USERS")
        print("-" * 30)
        
        self.expense_manager.add_user("alice", "Alice Johnson", "alice@email.com", "555-0101")
        self.expense_manager.add_user("bob", "Bob Smith", "bob@email.com", "555-0102")
        self.expense_manager.add_user("charlie", "Charlie Brown", "charlie@email.com", "555-0103")
        self.expense_manager.add_user("diana", "Diana Wilson", "diana@email.com", "555-0104")
    
    def _create_groups(self):
        """Create demo groups"""
        print("\n2️⃣ CREATING GROUPS")
        print("-" * 30)
        
        # Create groups
        self.roommates_group = self.expense_manager.create_group("Roommates", "Shared apartment expenses", "alice")
        self.vacation_group = self.expense_manager.create_group("Beach Vacation", "Summer 2024 trip", "bob")
        
        # Add users to groups
        self.expense_manager.add_users_to_group(self.roommates_group.group_id, ["alice", "bob", "charlie"])
        self.expense_manager.add_users_to_group(self.vacation_group.group_id, ["alice", "bob", "diana"])
    
    def _add_expenses(self):
        """Add demo expenses"""
        print("\n3️⃣ ADDING EXPENSES - EQUAL SPLITS")
        print("-" * 40)
        
        # Equal split example
        self.expense_manager.add_expense_equal_split(
            amount=150.0,
            paid_by_id="alice",
            participant_ids=["alice", "bob", "charlie"],
            description="Grocery shopping",
            category=ExpenseCategory.FOOD,
            group_id=self.roommates_group.group_id
        )
        
        print("\n4️⃣ ADDING EXPENSES - EXACT SPLITS")
        print("-" * 40)
        
        # Exact split example
        self.expense_manager.add_expense_exact_split(
            amount=200.0,
            paid_by_id="bob",
            user_amounts={"alice": 80.0, "bob": 60.0, "diana": 60.0},
            description="Hotel booking",
            category=ExpenseCategory.TRAVEL,
            group_id=self.vacation_group.group_id
        )
        
        print("\n5️⃣ ADDING EXPENSES - PERCENTAGE SPLITS")
        print("-" * 45)
        
        # Percentage split example
        self.expense_manager.add_expense_percent_split(
            amount=300.0,
            paid_by_id="charlie",
            user_percentages={"alice": 40.0, "bob": 35.0, "charlie": 25.0},
            description="Utilities bill",
            category=ExpenseCategory.UTILITIES,
            group_id=self.roommates_group.group_id
        )
        
        print("\n6️⃣ ADDING EXPENSES - MIXED SPLITS")
        print("-" * 40)
        
        # Mixed split example
        self.expense_manager.add_expense_mixed_split(
            amount=240.0,
            paid_by_id="diana",
            split_configs=[
                {"user_id": "alice", "type": "PERCENT", "percentage": 50.0},  # $120
                {"user_id": "bob", "type": "EXACT", "amount": 80.0},           # $80
                {"user_id": "diana", "type": "EQUAL"}                        # $40 (remaining)
            ],
            description="Restaurant dinner",
            category=ExpenseCategory.FOOD,
            group_id=self.vacation_group.group_id
        )
    
    def _show_balances(self):
        """Show balance summaries"""
        print("\n7️⃣ BALANCE SUMMARIES")
        print("-" * 30)
        
        # Show individual balances
        self.display_service.show_user_balances("alice")
        self.display_service.show_user_balances("bob")
        
        # Show group balances
        self.display_service.show_group_balances(self.roommates_group.group_id)
        self.display_service.show_group_balances(self.vacation_group.group_id)
    
    def _perform_settlements(self):
        """Perform settlements"""
        print("\n8️⃣ SETTLEMENTS")
        print("-" * 20)
        
        # Settle some debts
        self.expense_manager.settle_up("bob", "alice", 50.0, self.roommates_group.group_id)
        self.expense_manager.settle_up("charlie", "alice", 75.0)
        
        # Show updated balances
        print("\n📊 UPDATED BALANCES AFTER SETTLEMENTS:")
        self.display_service.show_user_balances("alice")
        self.display_service.show_user_balances("bob")
        self.display_service.show_user_balances("charlie")
    
    def _show_summaries(self):
        """Show comprehensive summaries"""
        print("\n9️⃣ GROUP SUMMARIES")
        print("-" * 30)
        
        # Show comprehensive group summaries
        self.display_service.show_group_summary(self.roommates_group.group_id)
        self.display_service.show_group_summary(self.vacation_group.group_id)
        
        print("\n🔟 SYSTEM OVERVIEW")
        print("-" * 25)
        
        self.display_service.show_all_balances()


def run_splitwise_demo():
    """Entry point for running the Splitwise demo"""
    demo = SplitWiseDemo()
    demo.run_demo()
    
    print(f"\n" + "=" * 60)
    print("🎯 KEY ENHANCEMENTS DEMONSTRATED:")
    print("1. ✅ User management with profiles and group memberships")
    print("2. ✅ Group creation and membership management") 
    print("3. ✅ Flexible expense splitting (equal, exact, percentage, mixed)")
    print("4. ✅ Group-specific and overall balance tracking")
    print("5. ✅ Advanced settlement system with group context")
    print("6. ✅ Comprehensive reporting and balance summaries")
    print("7. ✅ Category-based expense organization")
    print("8. ✅ Robust validation and error handling")
    
    return demo.expense_manager


if __name__ == "__main__":
    run_splitwise_demo()