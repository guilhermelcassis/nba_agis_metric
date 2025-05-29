import pandas as pd
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playercareerstats, commonteamroster, leaguestandings, commonplayerinfo
import datetime
import time
import os
from dateutil.relativedelta import relativedelta

def calculate_agis(player_stats, opp_win_pct=0.5):
    """
    Calculate AGIS metric for a player.
    
    AGIS = (PTS×1.0 + AST×1.8 + REB×1.2 + STL×2.5 + BLK×2.5 + EFF×0.7) 
           × [1 + ((opp_win_rate - 0.5) × 0.4)]
    
    Args:
        player_stats: Dictionary containing player statistics
        opp_win_pct: Opponent win percentage (default 0.5 as season average)
    """
    # Extract required stats
    pts = player_stats.get('points', 0)
    ast = player_stats.get('assists', 0)
    reb = player_stats.get('rebounds', 0)
    stl = player_stats.get('steals', 0)
    blk = player_stats.get('blocks', 0)
    eff = player_stats.get('efficiency', 0)
    
    # Calculate base score with proper weights
    base_score = (
        pts * 1.0 +
        ast * 1.8 +
        reb * 1.2 +
        stl * 2.5 +
        blk * 2.5 +
        eff * 0.7
    )
    
    # Calculate win rate multiplier
    win_rate_multiplier = 1 + ((opp_win_pct - 0.5) * 0.4)
    
    # Return AGIS score
    return base_score * win_rate_multiplier

def calculate_age(birthdate_str):
    """Calculate age from birthdate string in format 'YYYY-MM-DD'"""
    if not birthdate_str:
        return None
    try:
        birthdate = datetime.datetime.strptime(birthdate_str, '%Y-%m-%d')
        today = datetime.datetime.now()
        age = relativedelta(today, birthdate).years
        return age
    except Exception:
        return None

def get_all_nba_players(include_stats=True):
    """
    Fetch all NBA players (active and inactive) and save to Excel file
    
    Args:
        include_stats (bool): Whether to include player stats (takes longer)
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
    
    # Get team data
    all_teams = teams.get_teams()
    teams_df = pd.DataFrame(all_teams)
    teams_lookup = dict(zip(teams_df['id'], teams_df['full_name']))
    
    # Get league standings for team records
    try:
        print("Fetching current league standings...")
        standings = leaguestandings.LeagueStandings()
        standings_df = standings.get_data_frames()[0]
        
        # Create lookup for team win percentages
        team_win_pct = {}
        for _, row in standings_df.iterrows():
            team_id = row['TeamID']
            win_pct = row['WinPCT']
            team_win_pct[team_id] = win_pct
            
        print(f"Successfully fetched standings for {len(team_win_pct)} teams")
    except Exception as e:
        print(f"Error fetching standings: {str(e)}")
        team_win_pct = {}
    
    # Create directory for Excel files if it doesn't exist
    output_dir = 'nba_data'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create today's date string for filenames
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # If we want to include stats, fetch them for each active player
    if include_stats:
        print("Fetching player statistics (this may take a while)...")
        
        # Initialize lists to store player stats
        player_stats = []
        
        # For each active player, get their career stats
        for idx, player in active_players.iterrows():
            try:
                player_id = player['id']
                
                # Get player career stats
                career = playercareerstats.PlayerCareerStats(player_id=player_id)
                career_df = career.get_data_frames()[0]
                
                # Get player detailed info (demographics, physical data, etc.)
                player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
                info_df = player_info.get_data_frames()[0]
                
                if not career_df.empty and not info_df.empty:
                    # Get most recent season stats
                    recent_stats = career_df.iloc[-1]
                    player_details = info_df.iloc[0]
                    
                    # Calculate efficiency
                    eff = (
                        recent_stats.get('PTS', 0) + 
                        recent_stats.get('REB', 0) + 
                        recent_stats.get('AST', 0) + 
                        recent_stats.get('STL', 0) + 
                        recent_stats.get('BLK', 0) - 
                        recent_stats.get('TOV', 0)
                    )
                    
                    team_id = recent_stats.get('TEAM_ID')
                    
                    # Get team win percentage from standings or default to 0.5
                    team_win_percentage = team_win_pct.get(team_id, 0.5)
                    
                    # Extract player demographic info
                    birthdate = player_details.get('BIRTHDATE', '')
                    if birthdate and len(str(birthdate)) > 10:
                        birthdate = str(birthdate)[:10]
                    
                    # Calculate age from birthdate
                    age = calculate_age(birthdate)
                    
                    # Extract height in feet-inches and convert to separate fields
                    height_str = player_details.get('HEIGHT', '')
                    height_ft = None
                    height_in = None
                    if height_str and '-' in height_str:
                        try:
                            ft, inches = height_str.split('-')
                            height_ft = int(ft)
                            height_in = int(inches)
                        except Exception:
                            pass
                    
                    # Add player info and stats to list
                    stats_dict = {
                        'player_id': player_id,
                        'player_name': player['full_name'],
                        'birthdate': birthdate,
                        'age': age,
                        'position': player_details.get('POSITION', ''),
                        'height': player_details.get('HEIGHT', ''),
                        'height_ft': height_ft,
                        'height_in': height_in,
                        'weight': player_details.get('WEIGHT', ''),
                        'country': player_details.get('COUNTRY', ''),
                        'college': player_details.get('SCHOOL', ''),
                        'draft_year': player_details.get('DRAFT_YEAR', ''),
                        'draft_round': player_details.get('DRAFT_ROUND', ''),
                        'draft_number': player_details.get('DRAFT_NUMBER', ''),
                        'seasons_exp': player_details.get('SEASON_EXP', 0),
                        'jersey': player_details.get('JERSEY', ''),
                        'team_id': team_id,
                        'team_name': teams_lookup.get(team_id, 'Unknown'),
                        'team_city': player_details.get('TEAM_CITY', ''),
                        'team_abbreviation': player_details.get('TEAM_ABBREVIATION', ''),
                        'season': recent_stats.get('SEASON_ID'),
                        'games_played': recent_stats.get('GP'),
                        'games_started': recent_stats.get('GS'),
                        'minutes': recent_stats.get('MIN'),
                        'points': recent_stats.get('PTS'),
                        'rebounds': recent_stats.get('REB'),
                        'assists': recent_stats.get('AST'),
                        'steals': recent_stats.get('STL'),
                        'blocks': recent_stats.get('BLK'),
                        'turnovers': recent_stats.get('TOV'),
                        'fg_pct': recent_stats.get('FG_PCT'),
                        'fg3_pct': recent_stats.get('FG3_PCT'),
                        'ft_pct': recent_stats.get('FT_PCT'),
                        'efficiency': eff,
                        'team_win_pct': team_win_percentage
                    }
                    
                    # Calculate AGIS score using the proper formula
                    stats_dict['agis_score'] = calculate_agis(stats_dict, stats_dict['team_win_pct'])
                    
                    player_stats.append(stats_dict)
                
                # Pause to avoid hitting API rate limits
                time.sleep(0.6)
                
                # Print progress every 10 players
                if (idx + 1) % 10 == 0:
                    print(f"Processed {idx + 1} out of {len(active_players)} players")
                
            except Exception as e:
                print(f"Error processing player {player['full_name']}: {str(e)}")
        
        # Convert player stats to DataFrame
        if player_stats:
            stats_df = pd.DataFrame(player_stats)
            
            # Sort by AGIS score (descending)
            stats_df = stats_df.sort_values(by='agis_score', ascending=False)
            
            # Reorder columns for better readability
            column_order = [
                'player_id', 'player_name', 'age', 'position', 'height', 'weight',
                'team_name', 'team_abbreviation', 'jersey', 'country', 
                'seasons_exp', 'college', 'draft_year', 'draft_round', 'draft_number',
                'games_played', 'games_started', 'minutes',
                'points', 'rebounds', 'assists', 'steals', 'blocks', 'turnovers',
                'fg_pct', 'fg3_pct', 'ft_pct', 'efficiency', 'agis_score',
                'team_win_pct', 'birthdate', 'height_ft', 'height_in', 'team_id', 'team_city', 'season'
            ]
            
            # Ensure all columns exist, using only those that do
            existing_columns = [col for col in column_order if col in stats_df.columns]
            stats_df = stats_df[existing_columns]
            
            # Save player stats to Excel
            stats_filename = os.path.join(output_dir, f'nba_player_stats_{today}.xlsx')
            stats_df.to_excel(stats_filename, index=False)
            print(f"Successfully saved player statistics to {stats_filename}")
            
            # Also save a top players file
            top_players = stats_df.head(50)
            top_filename = os.path.join(output_dir, f'nba_top_players_by_agis_{today}.xlsx')
            top_players.to_excel(top_filename, index=False)
            print(f"Successfully saved top 50 players by AGIS to {top_filename}")
    
    # Get team rosters for current season
    print("Fetching current team rosters...")
    all_rosters = []
    
    for team in all_teams:
        if team['is_nba_team']:
            try:
                team_id = team['id']
                roster = commonteamroster.CommonTeamRoster(team_id=team_id)
                roster_df = roster.get_data_frames()[0]
                
                if not roster_df.empty:
                    # Add team info to the roster
                    roster_df['TEAM_NAME'] = team['full_name']
                    roster_df['TEAM_ABBREVIATION'] = team['abbreviation']
                    all_rosters.append(roster_df)
                
                # Pause to avoid hitting API rate limits
                time.sleep(0.6)
                
            except Exception as e:
                print(f"Error fetching roster for {team['full_name']}: {str(e)}")
    
    # Combine all rosters
    if all_rosters:
        combined_roster = pd.concat(all_rosters)
        roster_filename = os.path.join(output_dir, f'nba_team_rosters_{today}.xlsx')
        combined_roster.to_excel(roster_filename, index=False)
        print(f"Successfully saved team rosters to {roster_filename}")
    
    # Save active players list
    active_filename = os.path.join(output_dir, f'nba_active_players_{today}.xlsx')
    active_players.to_excel(active_filename, index=False)
    print(f"Successfully saved {len(active_players)} active NBA players to {active_filename}")
    
    # Save all players (including inactive)
    all_players_df = df.sort_values(by='last_name')
    all_players_df['full_name'] = all_players_df['first_name'] + ' ' + all_players_df['last_name']
    
    all_players_filename = os.path.join(output_dir, f'all_nba_players_{today}.xlsx')
    all_players_df.to_excel(all_players_filename, index=False)
    print(f"Successfully saved {len(all_players_df)} total NBA players to {all_players_filename}")
    
    # Save teams information
    teams_filename = os.path.join(output_dir, f'nba_teams_{today}.xlsx')
    teams_df.to_excel(teams_filename, index=False)
    print(f"Successfully saved {len(teams_df)} NBA teams to {teams_filename}")
    
    return active_players

if __name__ == "__main__":
    # Ask the user if they want to include player stats (which takes longer)
    include_stats = input("Include player statistics? (y/n, default=n): ").lower() == 'y'
    
    active_players = get_all_nba_players(include_stats=include_stats)
    
    print("\nProcess completed! Files have been saved to the 'nba_data' directory.") 