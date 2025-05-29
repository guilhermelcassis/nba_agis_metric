import sqlite3
import os
import pandas as pd
from tabulate import tabulate
import argparse

def connect_to_db():
    """Connect to the SQLite database"""
    db_path = os.path.join('nba_data', 'nba_players.db')
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        print("Please run create_nba_db.py first to create the database.")
        return None
    
    return sqlite3.connect(db_path)

def execute_query(query, params=None):
    """Execute a SQL query and return the results as a DataFrame"""
    conn = connect_to_db()
    if conn is None:
        return None
    
    try:
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        conn.close()
        return None

def show_tables():
    """List all tables in the database"""
    conn = connect_to_db()
    if conn is None:
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    
    print("Tables in the database:")
    for table in tables:
        print(f"- {table[0]}")

def show_schema(table_name):
    """Show the schema for a specific table"""
    conn = connect_to_db()
    if conn is None:
        return
    
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    conn.close()
    
    if not columns:
        print(f"Table '{table_name}' not found.")
        return
    
    print(f"Schema for table '{table_name}':")
    headers = ["Index", "Name", "Type", "NotNull", "DefaultValue", "PK"]
    print(tabulate(columns, headers=headers, tablefmt="grid"))

def top_players_by_salary(limit=10):
    """Show the top N players by salary"""
    query = """
    SELECT player_name, team_name, position, "salary 24-25" as salary
    FROM players
    WHERE salary IS NOT NULL AND salary > 0
    ORDER BY salary DESC
    LIMIT ?
    """
    
    df = execute_query(query, params=(limit,))
    if df is not None and not df.empty:
        # Format salary as currency
        df['salary'] = df['salary'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "")
        print(f"\nTop {limit} Players by Salary:")
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    else:
        print("No data found or error executing query.")

def players_by_team(team_name):
    """Show all players for a specific team"""
    query = """
    SELECT player_name, position, age, "salary 24-25" as salary
    FROM players
    WHERE team_name LIKE ?
    ORDER BY salary DESC
    """
    
    df = execute_query(query, params=(f"%{team_name}%",))
    if df is not None and not df.empty:
        # Format salary as currency
        df['salary'] = df['salary'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "")
        print(f"\nPlayers for '{team_name}':")
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    else:
        print(f"No players found for team matching '{team_name}'.")

def players_by_position(position):
    """Show top players for a specific position"""
    query = """
    SELECT player_name, team_name, position, age, "salary 24-25" as salary
    FROM players
    WHERE position LIKE ?
    ORDER BY salary DESC
    LIMIT 15
    """
    
    df = execute_query(query, params=(f"%{position}%",))
    if df is not None and not df.empty:
        # Format salary as currency
        df['salary'] = df['salary'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "")
        print(f"\nTop Players for position matching '{position}':")
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    else:
        print(f"No players found for position matching '{position}'.")

def custom_query(query):
    """Execute a custom SQL query"""
    df = execute_query(query)
    if df is not None and not df.empty:
        print("\nQuery Results:")
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    else:
        print("No results found or error executing query.")

def main():
    parser = argparse.ArgumentParser(description='Query the NBA Players database')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Tables command
    subparsers.add_parser('tables', help='List all tables in the database')
    
    # Schema command
    schema_parser = subparsers.add_parser('schema', help='Show schema for a table')
    schema_parser.add_argument('table', help='Table name')
    
    # Top players command
    top_parser = subparsers.add_parser('top', help='Show top players by salary')
    top_parser.add_argument('--limit', type=int, default=10, help='Number of players to show')
    
    # Team command
    team_parser = subparsers.add_parser('team', help='Show players for a specific team')
    team_parser.add_argument('name', help='Team name (partial match)')
    
    # Position command
    pos_parser = subparsers.add_parser('position', help='Show players for a specific position')
    pos_parser.add_argument('name', help='Position name (partial match)')
    
    # Custom query command
    query_parser = subparsers.add_parser('query', help='Execute a custom SQL query')
    query_parser.add_argument('sql', help='SQL query to execute')
    
    args = parser.parse_args()
    
    # If no command is provided, print help
    if args.command is None:
        parser.print_help()
        return
    
    # Execute the requested command
    if args.command == 'tables':
        show_tables()
    elif args.command == 'schema':
        show_schema(args.table)
    elif args.command == 'top':
        top_players_by_salary(args.limit)
    elif args.command == 'team':
        players_by_team(args.name)
    elif args.command == 'position':
        players_by_position(args.name)
    elif args.command == 'query':
        custom_query(args.sql)

if __name__ == "__main__":
    main() 