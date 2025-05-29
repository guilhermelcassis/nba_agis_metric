# NBA Players Database

This set of tools allows you to import NBA player data from CSV into a SQLite database and query the data using a command-line interface.

## Files

- `create_nba_db.py` - Script to create the SQLite database from the CSV file
- `query_nba_db.py` - CLI tool to query the database with various commands
- `nba_data/players--csv.csv` - Source CSV file with player data
- `nba_data/nba_players.db` - Generated SQLite database (after running create_nba_db.py)

## Requirements

- Python 3.6+
- pandas
- sqlite3
- tabulate (for query tool formatting)

Install the required packages with:

```bash
pip install pandas tabulate
```

## Creating the Database

To create the SQLite database from the CSV file:

```bash
python create_nba_db.py
```

This will:
1. Read the CSV file from `nba_data/players--csv.csv`
2. Clean and process the data
3. Create a SQLite database at `nba_data/nba_players.db`
4. Create a table named `players` with the data
5. Add indexes for faster querying

## Querying the Database

The `query_nba_db.py` script provides a command-line interface to query the database. Here are some examples:

### List all tables in the database

```bash
python query_nba_db.py tables
```

### Show the schema for a table

```bash
python query_nba_db.py schema players
```

### Show top players by salary

```bash
python query_nba_db.py top
```

Or specify a limit:

```bash
python query_nba_db.py top --limit 20
```

### Show players for a specific team

```bash
python query_nba_db.py team "Lakers"
```

### Show players for a specific position

```bash
python query_nba_db.py position "Guard"
```

### Execute a custom SQL query

```bash
python query_nba_db.py query "SELECT player_name, age, position FROM players WHERE age < 22 ORDER BY age"
```

## Using SQLite Directly

You can also interact with the database directly using the SQLite command-line tool:

```bash
sqlite3 nba_data/nba_players.db
```

Some useful commands in the SQLite shell:

- `.tables` - List all tables
- `.schema players` - Show the schema for the players table
- `.mode column` - Set output mode to columnar format
- `.headers on` - Show column headers
- `.quit` or `.exit` - Exit the SQLite shell

Example queries:

```sql
-- Top 10 highest paid players
SELECT player_name, team_name, "salary 24-25" 
FROM players 
ORDER BY "salary 24-25" DESC 
LIMIT 10;

-- Players from a specific team
SELECT player_name, position, "salary 24-25" 
FROM players 
WHERE team_name='Los Angeles Lakers';

-- Average salary by position
SELECT position, AVG("salary 24-25") as avg_salary 
FROM players 
WHERE "salary 24-25" > 0 
GROUP BY position 
ORDER BY avg_salary DESC;
```

## Data Fields

The database contains the following fields for each player:

- `player_id` - Unique ID for the player
- `player_name` - Full name of the player
- `age` - Player's age
- `position` - Player's position
- `height` - Player's height
- `weight` - Player's weight
- `team_name` - Current team name
- `team_abbreviation` - Current team abbreviation
- `jersey` - Jersey number
- `country` - Country of origin
- `seasons_exp` - Years of NBA experience
- `college` - College attended
- `draft_year` - Year drafted
- `draft_round` - Draft round
- `draft_number` - Draft pick number
- `birthdate` - Date of birth
- `team_id` - Team ID
- `salary 24-25` - Salary for the 2024-2025 season 