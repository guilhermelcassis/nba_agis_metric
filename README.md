# NBA AGIS Metric Calculator

This project calculates the AGIS (Advanced Game Impact Score) metric for NBA players, focusing on playoff games. The AGIS metric is a comprehensive scoring system that evaluates player performance while considering opponent strength.

## Formula

```
AGIS = (PTS×1.0 + AST×1.8 + REB×1.2 + STL×2.5 + BLK×2.5 + EFF×0.7) × [1 + ((win_rate_do_oponente - 0.5) × 0.4)]
```

Where:
- PTS: Points
- AST: Assists
- REB: Rebounds
- STL: Steals
- BLK: Blocks
- EFF: Efficiency Rating
- win_rate_do_oponente: Opponent's win rate

## Key Metrics

The project calculates several key performance and financial metrics:

### Performance Metrics

- **AGIS**: Advanced Game Impact Score - A comprehensive measure of a player's impact that weighs various statistics and adjusts for opponent strength
- **AGIS/G**: AGIS per Game - The average impact a player has per game played

### Financial Metrics

- **$/AGIS**: Dollars per AGIS point - How much a team is paying per unit of player impact (calculated as Salary ÷ AGIS). This metric shows the cost of each "impact unit" a player generates.

- **$/AGIS/G**: Dollars per AGIS per Game - This is the key value metric that measures cost efficiency of a player's game-by-game impact. Calculated as:
  ```
  $/AGIS/G = (Salary × Games) ÷ (AGIS × AGIS) = (Salary × Games) ÷ AGIS²
  ```

  This metric effectively tells you how much a team is paying for each square unit of impact over the season. By factoring in both games played and the square of impact (AGIS²), it rewards players who maintain consistent high performance over more games. Lower values indicate better value from a player's contract relative to their performance. It's particularly useful for:
  
  - Identifying undervalued players (those producing high impact at low cost)
  - Evaluating contract efficiency with an emphasis on sustained performance
  - Comparing players at different salary levels on an equal value basis
  - Penalizing players with high salaries but limited impact or playing time

## Requirements

- Python 3.x
- pandas
- nba_api

## Installation

1. Clone the repository:
```bash
git clone https://github.com/guilhermelcassis/nba_agis_metric.git
cd nba
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the script to calculate AGIS metrics for NBA playoff games:
```bash
python nba_agis_metric.py
```

The script will:
1. Fetch player game logs for the specified date
2. Calculate efficiency metrics
3. Get opponent team records
4. Calculate the AGIS score
5. Display the top 10 players by AGIS score

## Author

Guilherme Cassis
- GitHub: [guilhermelcassis](https://github.com/guilhermelcassis) 