import pandas as pd
from nba_api.stats.static import players
import datetime
import os

def get_simple_player_list():
    """
    A simplified script to quickly fetch just the list of active NBA players
    and save to an Excel file without additional stats or details.
    """
    print("Fetching NBA players data...")
    
    # Get all players from the NBA API
    all_players = players.get_players()
    
    # Convert to DataFrame
    df = pd.DataFrame(all_players)
    
    # Get active players only
    active_players = df[df['is_active'] == True].copy()
    
    # Sort by last name
    active_players = active_players.sort_values(by='last_name')
    
    # Add full name column
    active_players['full_name'] = active_players['first_name'] + ' ' + active_players['last_name']
    
    # Reorder columns for better readability
    cols = ['id', 'full_name', 'first_name', 'last_name', 'is_active']
    active_players = active_players[cols]
    
    # Create output directory if it doesn't exist
    if not os.path.exists('nba_data'):
        os.makedirs('nba_data')
    
    # Save to Excel with current date
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f'nba_data/nba_players_simple_{today}.xlsx'
    
    active_players.to_excel(filename, index=False)
    print(f"Successfully saved {len(active_players)} active NBA players to {filename}")
    
    return active_players

if __name__ == "__main__":
    active_players = get_simple_player_list()
    
    # Display sample of active players
    print("\nSample of active players:")
    print(active_players.head(10)) 