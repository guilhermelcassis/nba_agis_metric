from flask import Flask, render_template, request, url_for
from nba_agis_metric import calculate_agis, get_team_record, TEAM_NAMES
from nba_api.stats.endpoints import playergamelogs
import pandas as pd
from datetime import datetime, timedelta
import os
import sqlite3

app = Flask(__name__, static_folder='static')

def get_player_salary(player_name):
    """Get the player's salary from the SQLite database."""
    try:
        db_path = os.path.join('nba_data', 'nba_players.db')
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}")
            return 0
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Use parameterized query to avoid SQL injection
        cursor.execute(
            'SELECT "salary 24-25" FROM players WHERE player_name = ?', 
            (player_name,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            # Return as integer, not formatted string
            return int(float(result[0]))
        else:
            return 0
    except Exception as e:
        print(f"Error fetching player salary: {str(e)}")
        return 0

def get_player_details(player_name):
    """Get detailed player information from the SQLite database."""
    try:
        db_path = os.path.join('nba_data', 'nba_players.db')
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}")
            return None
            
        conn = sqlite3.connect(db_path)
        
        # Use parameterized query to avoid SQL injection
        query = """
        SELECT player_id, player_name, age, position, height, weight, 
               team_name, team_abbreviation, jersey, country, 
               seasons_exp, college, draft_year, draft_round, draft_number, 
               birthdate, "salary 24-25" as salary
        FROM players 
        WHERE player_name = ?
        """
        
        df = pd.read_sql_query(query, conn, params=(player_name,))
        conn.close()
        
        if not df.empty:
            player_data = df.iloc[0].to_dict()
            
            # Format salary as currency without decimal places
            if pd.notnull(player_data.get('salary')):
                player_data['salary'] = f"${int(float(player_data['salary'])):,}"
            else:
                player_data['salary'] = "N/A"
                
            return player_data
        else:
            return None
    except Exception as e:
        print(f"Error fetching player details: {str(e)}")
        return None

def get_player_stats(filters=None, sort_by="agis_score", direction="desc"):
    """Get player stats from the SQLite database with optional filtering and sorting."""
    try:
        db_path = os.path.join('nba_data', 'nba_players.db')
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}")
            return None
            
        conn = sqlite3.connect(db_path)
        
        query = "SELECT * FROM player_stats_view"
        params = []
        
        # Apply filters if provided
        if filters:
            where_clauses = []
            
            if filters.get('team'):
                where_clauses.append("team_name LIKE ?")
                params.append(f"%{filters['team']}%")
                
            if filters.get('position'):
                where_clauses.append("position LIKE ?")
                params.append(f"%{filters['position']}%")
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
        
        # Apply sorting
        if sort_by:
            query += f" ORDER BY {sort_by} {'ASC' if direction == 'asc' else 'DESC'}"
        
        # Execute the query
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if not df.empty:
            # Process data to ensure salary_per_agis and salary_agis_per_game are proper types
            for idx, row in df.iterrows():
                # Convert salary_per_agis to float
                if pd.isna(df.at[idx, 'salary_per_agis']) or df.at[idx, 'salary_per_agis'] == 'N/A' or df.at[idx, 'salary_per_agis'] == 'DIV/0':
                    df.at[idx, 'salary_per_agis'] = 0.0
                else:
                    try:
                        df.at[idx, 'salary_per_agis'] = float(df.at[idx, 'salary_per_agis'])
                    except (ValueError, TypeError):
                        df.at[idx, 'salary_per_agis'] = 0.0
                
                # Convert salary_agis_per_game to float
                if pd.isna(df.at[idx, 'salary_agis_per_game']) or df.at[idx, 'salary_agis_per_game'] == 'N/A' or df.at[idx, 'salary_agis_per_game'] == 'DIV/0':
                    df.at[idx, 'salary_agis_per_game'] = 0.0
                else:
                    try:
                        df.at[idx, 'salary_agis_per_game'] = float(df.at[idx, 'salary_agis_per_game'])
                    except (ValueError, TypeError):
                        df.at[idx, 'salary_agis_per_game'] = 0.0
            
            return df.to_dict('records')
        else:
            return []
            
    except Exception as e:
        print(f"Error fetching player stats: {str(e)}")
        return []

def get_player_stats_by_id(player_id):
    """Get detailed stats for a specific player by ID."""
    try:
        db_path = os.path.join('nba_data', 'nba_players.db')
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}")
            return None
            
        conn = sqlite3.connect(db_path)
        
        query = "SELECT * FROM player_stats_view WHERE player_id = ?"
        
        df = pd.read_sql_query(query, conn, params=(player_id,))
        conn.close()
        
        if not df.empty:
            # Process salary_per_agis and salary_agis_per_game
            row = df.iloc[0]
            player_data = row.to_dict()
            
            # Convert salary_per_agis to float
            if pd.isna(row['salary_per_agis']) or row['salary_per_agis'] == 'N/A' or row['salary_per_agis'] == 'DIV/0':
                player_data['salary_per_agis'] = 0.0
            else:
                try:
                    player_data['salary_per_agis'] = float(row['salary_per_agis'])
                except (ValueError, TypeError):
                    player_data['salary_per_agis'] = 0.0
            
            # Convert salary_agis_per_game to float
            if pd.isna(row['salary_agis_per_game']) or row['salary_agis_per_game'] == 'N/A' or row['salary_agis_per_game'] == 'DIV/0':
                player_data['salary_agis_per_game'] = 0.0
            else:
                try:
                    player_data['salary_agis_per_game'] = float(row['salary_agis_per_game'])
                except (ValueError, TypeError):
                    player_data['salary_agis_per_game'] = 0.0
            
            return player_data
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching player stats by ID: {str(e)}")
        return None

def get_unique_values(column):
    """Get unique values for a specific column from the player stats view."""
    try:
        db_path = os.path.join('nba_data', 'nba_players.db')
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}")
            return []
            
        conn = sqlite3.connect(db_path)
        
        query = f"SELECT DISTINCT {column} FROM player_stats_view WHERE {column} IS NOT NULL ORDER BY {column}"
        
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return [r[0] for r in results if r[0]]
            
    except Exception as e:
        print(f"Error fetching unique values for {column}: {str(e)}")
        return []

def get_games_by_date_range(start_date, end_date):
    """Get player game logs for the specified date range."""
    try:
        # Convert dates to the format expected by the NBA API
        start_date_str = datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y')
        end_date_str = datetime.strptime(end_date, '%Y-%m-%d').strftime('%m/%d/%Y')
        
        games_df = playergamelogs.PlayerGameLogs(
            season_nullable='2024-25',
            season_type_nullable='Playoffs',
            date_from_nullable=start_date_str,
            date_to_nullable=end_date_str
        ).player_game_logs.get_data_frame()
        
        if games_df.empty:
            return None
            
        # Print available columns for debugging
        print("\nAvailable columns:")
        print(games_df.columns.tolist())
            
        # Format the game date
        games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE']).dt.strftime('%Y-%m-%d')
        
        # Calculate efficiency
        games_df['EFF'] = (
            games_df['PTS'] + games_df['REB'] + games_df['AST'] + 
            games_df['STL'] + games_df['BLK'] - 
            (games_df['TOV'] + (games_df['FGA'] - games_df['FGM']) + 
             (games_df['FTA'] - games_df['FTM']))
        )
        
        # Get opponent information
        games_df['OPP_TEAM'] = games_df['MATCHUP'].apply(
            lambda x: x.split(' ')[-1] if '@' in x else x.split(' ')[0]
        )
        
        # Get team records
        for team_abbr in games_df['OPP_TEAM'].unique():
            team_name = TEAM_NAMES.get(team_abbr, "Unknown Team")
            record, win_pct = get_team_record(team_name)
            games_df.loc[games_df['OPP_TEAM'] == team_abbr, 'OPP_RECORD'] = record
            games_df.loc[games_df['OPP_TEAM'] == team_abbr, 'OPP_WL_RATIO'] = win_pct
        
        # Calculate AGIS
        games_df['AGIS'] = games_df.apply(calculate_agis, axis=1)
        
        # Add salary information for each player
        games_df['SALARY'] = games_df['PLAYER_NAME'].apply(get_player_salary)
        
        # Prepare results with all available stats
        result_df = games_df[['PLAYER_NAME', 'GAME_DATE', 'MATCHUP', 'OPP_RECORD', 'MIN_SEC',
                            'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS',
                            'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'EFF', 'AGIS', 'SALARY']]
        
        # Convert percentage columns to float and format them
        for col in ['FG_PCT', 'FG3_PCT', 'FT_PCT']:
            result_df[col] = result_df[col].fillna(0).astype(float)
        
        return result_df.sort_values(by='AGIS', ascending=False)
        
    except Exception as e:
        print(f"Error fetching games: {str(e)}")
        return None

@app.route('/')
def index():
    """Main page showing top performers for selected date range."""
    # Get date range from query parameters or use default (today)
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = request.args.get('start_date', yesterday)
    end_date = request.args.get('end_date', today)
    
    games_df = get_games_by_date_range(start_date, end_date)
    
    if games_df is None or games_df.empty:
        return render_template('index.html', 
                             start_date=start_date,
                             end_date=end_date,
                             message="No games found for the selected date range",
                             players=None)
    
    # Get top 20 players
    top_players = games_df.head(20).to_dict('records')
    
    return render_template('index.html',
                         start_date=start_date,
                         end_date=end_date,
                         message="Top 20 Players by AGIS Score",
                         players=top_players)

@app.route('/player-stats')
def player_stats():
    """Display player statistics for the 2024-25 season."""
    # Get filter parameters
    team = request.args.get('team', '')
    position = request.args.get('position', '')
    sort_by = request.args.get('sort_by', 'agis_score')
    direction = request.args.get('direction', 'desc')
    
    # Build filters dictionary
    filters = {}
    if team:
        filters['team'] = team
    if position:
        filters['position'] = position
    
    # Get player stats with filters
    players = get_player_stats(filters, sort_by, direction)
    
    # Get unique values for filter dropdowns
    teams = get_unique_values('team_name')
    positions = get_unique_values('position')
    
    return render_template('player_stats.html',
                          players=players,
                          teams=teams,
                          positions=positions,
                          selected_team=team,
                          selected_position=position,
                          sort_by=sort_by,
                          direction=direction)

@app.route('/player-details/<player_id>')
def player_details_stats(player_id):
    """Display detailed stats for a specific player."""
    player = get_player_stats_by_id(player_id)
    
    if not player:
        return render_template('index.html',
                             message=f"Player not found with ID {player_id}",
                             players=None)
    
    return render_template('player_details_stats.html', player=player)

@app.route('/player/<player_name>/<game_date>')
def player_details(player_name, game_date):
    """Display detailed stats for a specific player's game and all other games from the season."""
    try:
        # Parse the selected game date
        game_date_obj = datetime.strptime(game_date, '%Y-%m-%d')
        
        # For the selected game, use the exact date
        start_date = game_date
        end_date = game_date
        
        # Get the specific game
        selected_game_df = get_games_by_date_range(start_date, end_date)
        
        if selected_game_df is None or selected_game_df.empty:
            return render_template('index.html',
                                 message=f"No games found for {player_name} on {game_date}",
                                 players=None)
        
        # Find the specific player's game
        player_selected_game = selected_game_df[selected_game_df['PLAYER_NAME'] == player_name]
        
        if player_selected_game.empty:
            return render_template('index.html',
                                 message=f"No game found for {player_name} on {game_date}",
                                 players=None)
        
        # Get the player's game data for the selected date
        selected_game_data = player_selected_game.iloc[0].to_dict()
        
        # Get additional player details from the database
        db_player_details = get_player_details(player_name)
        
        # Now get all games for this player in the season
        # Use a wider date range for the season - adjust as needed for your data
        season_start = "2024-10-01"  # Start of 2024-25 season
        season_end = datetime.now().strftime('%Y-%m-%d')  # Today's date
        
        all_games_df = get_games_by_date_range(season_start, season_end)
        
        if all_games_df is not None and not all_games_df.empty:
            # Filter for just this player's games
            player_all_games = all_games_df[all_games_df['PLAYER_NAME'] == player_name]
            
            # Sort by date (descending - most recent first)
            player_all_games = player_all_games.sort_values(by='GAME_DATE', ascending=False)
            
            # Convert to list of dicts for the template
            all_games = player_all_games.to_dict('records')
        else:
            all_games = []
            
        return render_template('player_details.html', 
                              player=selected_game_data,
                              player_db=db_player_details,
                              all_games=all_games,
                              selected_date=game_date)
        
    except Exception as e:
        print(f"Error retrieving player details: {str(e)}")
        return render_template('index.html',
                             message=f"Error retrieving details for {player_name}: {str(e)}",
                             players=None)

if __name__ == '__main__':
    app.run(debug=True) 