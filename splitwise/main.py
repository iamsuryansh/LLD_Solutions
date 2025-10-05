#!/usr/bin/env python3
"""
Main entry point for Splitwise Service
Provides backward compatibility with the original single-file design
"""

# Import all components from the modular architecture
from src import *

# For backward compatibility, expose main classes at module level
__version__ = "2.0.0" 
__author__ = "LLD Practice"

def create_splitwise_service() -> ExpenseManager:
    """
    Factory function to create a configured Splitwise ExpenseManager instance
    
    Returns:
        Configured ExpenseManager instance with all managers
    """
    return ExpenseManager()


def main():
    """
    Main entry point - runs the comprehensive demo
    """
    from demo.demo_runner import run_splitwise_demo
    run_splitwise_demo()

if __name__ == "__main__":
    main()