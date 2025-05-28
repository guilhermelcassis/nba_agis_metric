import pandas as pd
from nba_api.stats.endpoints import playergamelogs, teamgamelog
from nba_api.stats.static import teams
import time

# Display settings
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# Team name mapping
TEAM_NAMES = {
    'ATL': 'Atlanta Hawks', 'BOS': 'Boston Celtics', 'BKN': 'Brooklyn Nets',
    'CHA': 'Charlotte Hornets', 'CHI': 'Chicago Bulls', 'CLE': 'Cleveland Cavaliers',
    'DAL': 'Dallas Mavericks', 'DEN': 'Denver Nuggets', 'DET': 'Detroit Pistons',
    'GSW': 'Golden State Warriors', 'HOU': 'Houston Rockets', 'IND': 'Indiana Pacers',
    'LAC': 'Los Angeles Clippers', 'LAL': 'Los Angeles Lakers', 'MEM': 'Memphis Grizzlies',
    'MIA': 'Miami Heat', 'MIL': 'Milwaukee Bucks', 'MIN': 'Minnesota Timberwolves',
    'NOP': 'New Orleans Pelicans', 'NYK': 'New York Knicks', 'OKC': 'Oklahoma City Thunder',
    'ORL': 'Orlando Magic', 'PHI': 'Philadelphia 76ers', 'PHX': 'Phoenix Suns',
    'POR': 'Portland Trail Blazers', 'SAC': 'Sacramento Kings', 'SAS': 'San Antonio Spurs',
    'TOR': 'Toronto Raptors', 'UTA': 'Utah Jazz', 'WAS': 'Washington Wizards'
}

def get_team_record(team_name, season='2024-25', season_type='Playoffs'):
    """Get team's win-loss record and win percentage."""
    # Find team ID
    team_dict = [team for team in teams.get_teams() 
                 if team['full_name'].lower() == team_name.lower()]
    
    if not team_dict:
        return "N/A", 0.0
    
    # Get team game log with retry mechanism
    for attempt in range(3):
        try:
            gamelog = teamgamelog.TeamGameLog(
                team_id=team_dict[0]['id'],
                season=season,
                season_type_all_star=season_type
            ).get_data_frames()[0]
            
            wins = len(gamelog[gamelog['WL'] == 'W'])
            losses = len(gamelog[gamelog['WL'] == 'L'])
            total_games = wins + losses
            win_percentage = wins / total_games if total_games > 0 else 0
            
            return f"{wins}-{losses} ({win_percentage:.3f})", win_percentage
            
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return "API Error", 0.0

def calculate_agis(row):
    """Calculate AGIS metric for a player.
    
    AGIS = (PTS×1.0 + AST×1.8 + REB×1.2 + STL×2.5 + BLK×2.5 + EFF×0.7) 
           × [1 + ((opp_win_rate - 0.5) × 0.4)]
    """
    base_score = (
        row['PTS'] * 1.0 +
        row['AST'] * 1.8 +
        row['REB'] * 1.2 +
        row['STL'] * 2.5 +
        row['BLK'] * 2.5 +
        row['EFF'] * 0.7
    )
    
    win_rate_multiplier = 1 + ((row['OPP_WL_RATIO'] - 0.5) * 0.4)
    return base_score * win_rate_multiplier

def main():
    try:
        # Get player game logs
        print("\nFetching player game logs...")
        games_df = playergamelogs.PlayerGameLogs(
            season_nullable='2024-25',
            season_type_nullable='Playoffs',
            date_from_nullable='05/20/2025',
            date_to_nullable='06/02/2025'
        ).player_game_logs.get_data_frame()

        # Format the game date to remove time component
        games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE']).dt.strftime('%Y-%m-%d')

        # Calculate efficiency
        print("\nCalculating efficiency metrics...")
        games_df['EFF'] = (
            games_df['PTS'] + games_df['REB'] + games_df['AST'] + 
            games_df['STL'] + games_df['BLK'] - 
            (games_df['TOV'] + (games_df['FGA'] - games_df['FGM']) + 
             (games_df['FTA'] - games_df['FTM']))
        )

        # Get opponent information
        print("Processing opponent data...")
        games_df['OPP_TEAM'] = games_df['MATCHUP'].apply(
            lambda x: x.split(' ')[-1] if '@' in x else x.split(' ')[0]
        )

        # Get team records
        for team_abbr in games_df['OPP_TEAM'].unique():
            team_name = TEAM_NAMES.get(team_abbr, "Unknown Team")
            record, win_pct = get_team_record(team_name)
            games_df.loc[games_df['OPP_TEAM'] == team_abbr, 'OPP_RECORD'] = record
            games_df.loc[games_df['OPP_TEAM'] == team_abbr, 'OPP_WL_RATIO'] = win_pct
            time.sleep(1)  # Respect API rate limits

        # Calculate AGIS
        print("Calculating AGIS scores...")
        games_df['AGIS'] = games_df.apply(calculate_agis, axis=1)

        # Prepare final results
        result_df = games_df[['PLAYER_NAME', 'GAME_DATE', 'MATCHUP', 'OPP_RECORD', 'MIN',
                            'PTS', 'REB', 'AST', 'STL', 'BLK', 'EFF', 'AGIS']]
        result_df = result_df.sort_values(by='AGIS', ascending=False)

        # Display results
        print("\nTop 20 players during the Conference Finals by AGIS score:")
        print("=" * 100)
        print(result_df.head(20).to_string(index=False))
        print("=" * 100)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 