# NBA Data Collection Tools

This collection of scripts allows you to fetch NBA player and team data and save it to Excel files for analysis.

## Features

- Fetch active NBA players list
- Get detailed player statistics
- Calculate AGIS scores for players (Advanced Game Impact Score)
- Retrieve team rosters
- Get team information
- Include player demographics (age, position, height, weight)
- Include player career information (college, draft data, experience)
- Save all data to Excel files with timestamps

## Requirements

- Python 3.6 or higher
- Required packages:
  - pandas
  - nba_api
  - openpyxl (for Excel support)
  - python-dateutil (for age calculation)

## Installation

1. Make sure you have Python installed
2. Install required packages:
   ```
   pip install pandas nba_api openpyxl python-dateutil
   ```

## Usage

### Option 1: Use the Launcher Script

The easiest way to run the tools is through the launcher script:

```
python get_nba_data.py
```

This will display a menu with options to:
1. Get a quick list of NBA players (fast)
2. Get detailed NBA data including player stats, rosters, etc. (slower)

### Option 2: Run Individual Scripts

#### For a simple player list (fast):

```
python get_simple_player_list.py
```

This creates a file named `nba_players_simple_YYYY-MM-DD.xlsx` in the `nba_data` directory.

#### For detailed data (slower):

```
python get_nba_players.py
```

This script will ask if you want to include player statistics. Including stats takes longer because the script needs to make more API calls.

It creates several files in the `nba_data` directory:
- `nba_active_players_YYYY-MM-DD.xlsx` - List of active NBA players
- `all_nba_players_YYYY-MM-DD.xlsx` - List of all NBA players (active and inactive)
- `nba_teams_YYYY-MM-DD.xlsx` - NBA teams information
- `nba_team_rosters_YYYY-MM-DD.xlsx` - Current team rosters
- `nba_player_stats_YYYY-MM-DD.xlsx` - Player statistics with AGIS scores
- `nba_top_players_by_agis_YYYY-MM-DD.xlsx` - Top 50 players ranked by AGIS score

## Player Data Included

The player statistics file includes comprehensive data for each player:

### Player Demographics
- Player name
- Age (calculated from birthdate)
- Position
- Height (in feet and inches)
- Weight
- Country of origin
- College/School

### Career Information
- Draft year
- Draft round
- Draft pick number
- Seasons of experience
- Jersey number

### Team Information
- Current team name
- Team abbreviation
- Team city

### Performance Statistics
- Games played
- Games started
- Minutes played
- Points
- Rebounds
- Assists
- Steals
- Blocks
- Turnovers
- Field goal percentage
- Three-point percentage
- Free throw percentage
- Efficiency score
- AGIS score

## About AGIS Score

The AGIS (Advanced Game Impact Score) is a metric that measures a player's overall impact. The formula is:

```
AGIS = (PTS×1.0 + AST×1.8 + REB×1.2 + STL×2.5 + BLK×2.5 + EFF×0.7) × [1 + ((opp_win_rate - 0.5) × 0.4)]
```

Where:
- PTS = Points
- AST = Assists
- REB = Rebounds
- STL = Steals
- BLK = Blocks
- EFF = Efficiency (PTS + REB + AST + STL + BLK - TOV)
- opp_win_rate = Opponent's win percentage (or team win percentage for season stats)

The AGIS score weights different statistics based on their impact on the game and also considers the strength of the opponent through their win percentage.

## Notes

- The scripts use the official NBA API
- Rate limiting is in place to avoid overwhelming the API
- Files are timestamped with the current date
- All data is saved in a folder called `nba_data`

## Troubleshooting

If you encounter any issues:

1. Make sure all required packages are installed
2. Check your internet connection
3. The NBA API may occasionally be down or change - if persistent issues occur, check for updates to the nba_api package 