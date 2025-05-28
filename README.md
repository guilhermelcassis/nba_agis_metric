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

## Requirements

- Python 3.x
- pandas
- nba_api

## Installation

1. Clone the repository:
```bash
git clone https://github.com/guilhermelcassis/nba.git
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