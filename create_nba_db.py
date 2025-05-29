import sqlite3
import pandas as pd
import os

def create_nba_database():
    # Define the path to the CSV file and the database
    csv_path = os.path.join('nba_data', 'players--csv.csv')
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
        
        # Clean the salary column - remove " $ " and "," characters and convert to numeric
        if 'salary 24-25' in df.columns:
            df['salary 24-25'] = df['salary 24-25'].str.replace('$', '').str.replace(',', '').str.strip() if hasattr(df['salary 24-25'], 'str') else df['salary 24-25']
            df['salary 24-25'] = pd.to_numeric(df['salary 24-25'], errors='coerce')
        
        # Connect to SQLite database (creates it if it doesn't exist)
        print(f"Creating database at {db_path}...")
        conn = sqlite3.connect(db_path)
        
        # Write the data to a SQLite table
        df.to_sql('players', conn, if_exists='replace', index=False)
        
        # Create indexes on commonly queried columns for better performance
        cursor = conn.cursor()
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_id ON players(player_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_name ON players(player_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_id ON players(team_id)')
        conn.commit()
        
        # Verify that the data was written
        result = conn.execute("SELECT COUNT(*) FROM players").fetchone()
        print(f"Successfully created database with {result[0]} player records")
        
        # Close the connection
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        return False

if __name__ == "__main__":
    create_nba_database()
    
    # Provide examples of how to query the database
    print("\nExample queries you can run:")
    print("1. Connect to the database: sqlite3 nba_data/nba_players.db")
    print("2. List all tables: .tables")
    print("3. Show schema: .schema players")
    print("4. Query top 10 highest paid players: SELECT player_name, team_name, \"salary 24-25\" FROM players ORDER BY \"salary 24-25\" DESC LIMIT 10;")
    print("5. Query players by team: SELECT player_name, position, \"salary 24-25\" FROM players WHERE team_name='Los Angeles Lakers';")
    print("6. Exit SQLite: .exit") 