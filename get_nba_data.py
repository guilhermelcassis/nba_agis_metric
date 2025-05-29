"""
NBA Data Collection Tool

This script serves as a launcher for the NBA data collection tools.
It allows the user to choose between:
1. Quick player list - Just active player names (fast)
2. Detailed player data - Players, teams, rosters, and stats (slower)
"""

import os
import sys

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    """Display the main menu and get user choice"""
    clear_screen()
    print("=== NBA DATA COLLECTION TOOL ===")
    print()
    print("Choose an option:")
    print("1. Quick player list (just names, fast)")
    print("2. Detailed player & team data (includes stats, slower)")
    print("3. Exit")
    print()
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == "1":
        clear_screen()
        print("Running quick player list...")
        print("="*50)
        from get_simple_player_list import get_simple_player_list
        get_simple_player_list()
    
    elif choice == "2":
        clear_screen()
        print("Running detailed data collection...")
        print("="*50)
        from get_nba_players import get_all_nba_players
        
        include_stats = input("Include player statistics? This will take longer (y/n, default=n): ").lower() == 'y'
        get_all_nba_players(include_stats=include_stats)
    
    elif choice == "3":
        print("Exiting...")
        sys.exit(0)
    
    else:
        print("Invalid choice. Please try again.")
        input("Press Enter to continue...")
        main_menu()
    
    # After execution, prompt to return to menu or exit
    print("\nData collection complete!")
    again = input("\nReturn to main menu? (y/n, default=y): ").lower() != 'n'
    
    if again:
        main_menu()
    else:
        print("Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import pandas as pd
        from nba_api.stats.static import players
    except ImportError:
        print("Required packages are missing. Installing...")
        os.system("pip install pandas openpyxl nba_api")
        print("Packages installed. Starting application...")
    
    # Create output directory if it doesn't exist
    if not os.path.exists('nba_data'):
        os.makedirs('nba_data')
    
    # Show the main menu
    main_menu() 