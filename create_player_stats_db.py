import sqlite3
import pandas as pd
import os

def create_player_stats_database():
    # Define the path to the CSV file and the database
    csv_path = os.path.join('nba_data', 'players stats 24-25 csv.csv')
    db_path = os.path.join('nba_data', 'nba_players.db')
    
    # Check if the CSV file exists
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return False
    
    print(f"Reading data from {csv_path}...")
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Display info about the data
        print(f"Loaded {len(df)} player records with {len(df.columns)} fields")
        print(f"Columns: {', '.join(df.columns)}")
        
        # Clean the data - handle any potential issues
        # Strip whitespace from string columns
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.strip() if hasattr(df[col], 'str') else df[col]
        
        # Rename duplicate column
        if 'agis_score' in df.columns and 'agis_score.1' in df.columns:
            df = df.rename(columns={'agis_score.1': 'agis_score_alt'})
        
        # Connect to SQLite database
        print(f"Connecting to database at {db_path}...")
        conn = sqlite3.connect(db_path)
        
        # Write the data to a SQLite table
        df.to_sql('player_stats', conn, if_exists='replace', index=False)
        
        # Create indexes on commonly queried columns for better performance
        cursor = conn.cursor()
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_player_id ON player_stats(player_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_player_name ON player_stats(player_name)')
        conn.commit()
        
        # Verify that the data was written
        result = conn.execute("SELECT COUNT(*) FROM player_stats").fetchone()
        print(f"Successfully created player_stats table with {result[0]} records")
        
        # Create a view that joins player stats with player details
        print("Creating player_stats_view...")
        create_view_query = """
        CREATE VIEW IF NOT EXISTS player_stats_view AS
        SELECT 
            ps.player_id,
            ps.player_name,
            ps.games_played,
            ps.games_started,
            ps.minutes,
            ps.points,
            ps.rebounds,
            ps.assists,
            ps.steals,
            ps.blocks,
            ps.turnovers,
            ps.fg_pct,
            ps.fg3_pct,
            ps.ft_pct,
            ps.efficiency,
            ps.agis_score,
            ps."salary 24-25" as salary,
            ps.agis_per_game,
            ps."salary per AGIS" as salary_per_agis,
            ps."salary agis per game" as salary_agis_per_game,
            p.age,
            p.position,
            p.height,
            p.weight,
            p.team_name,
            p.team_abbreviation,
            p.jersey,
            p.country,
            p.seasons_exp,
            p.college,
            p.draft_year,
            p.draft_round,
            p.draft_number
        FROM 
            player_stats ps
        LEFT JOIN 
            players p ON ps.player_id = p.player_id
        """
        conn.execute(create_view_query)
        conn.commit()
        
        # Close the connection
        conn.close()
        
        print("Database update completed successfully.")
        return True
    
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        return False

if __name__ == "__main__":
    create_player_stats_database() 