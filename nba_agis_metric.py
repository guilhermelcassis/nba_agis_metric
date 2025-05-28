import pandas as pd
from nba_api.stats.endpoints import playergamelogs
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelog
import time

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)  # Para melhor visualização no terminal

# Cache para registros das equipes
team_record_cache = {}

def get_team_record(team_name, season='2024-25', season_type='Playoffs'):
    """Obtém o registro de vitórias de uma equipe para a temporada especificada."""
    # Verifica se já está no cache
    cache_key = f"{team_name}_{season}_{season_type}"
    if cache_key in team_record_cache:
        return team_record_cache[cache_key]
    
    # Encontra o ID da equipe baseado no nome
    nba_teams = teams.get_teams()
    team_dict = [team for team in nba_teams if team['full_name'].lower() == team_name.lower()]
    
    if not team_dict:
        record_str = "N/A"
        win_pct = 0.0
        team_record_cache[cache_key] = (record_str, win_pct)
        return team_record_cache[cache_key]
    
    team_id = team_dict[0]['id']
    
    # Tenta obter o log de jogos da equipe com mecanismo de retry
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Obtém o log de jogos da equipe para a temporada especificada
            gamelog = teamgamelog.TeamGameLog(
                team_id=team_id,
                season=season,
                season_type_all_star=season_type
            ).get_data_frames()[0]
            
            # Conta vitórias e derrotas
            wins = len(gamelog[gamelog['WL'] == 'W'])
            losses = len(gamelog[gamelog['WL'] == 'L'])
            
            # Calcula a porcentagem de vitórias
            total_games = wins + losses
            win_percentage = wins / total_games if total_games > 0 else 0
            
            record_str = f"{wins}-{losses} ({win_percentage:.3f})"
            # Armazena no cache
            team_record_cache[cache_key] = (record_str, win_percentage)
            return team_record_cache[cache_key]
            
        except Exception as e:
            print(f"Tentativa {attempt+1}/{max_retries} falhou para {team_name}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                record_str = "API Error"
                win_pct = 0.0
                team_record_cache[cache_key] = (record_str, win_pct)
                return team_record_cache[cache_key]

# Mapeamento de abreviação para nome completo da equipe
team_abbr_map = {
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

def get_full_team_name(abbr):
    """Converte a abreviação da equipe para o nome completo."""
    return team_abbr_map.get(abbr, "Unknown Team")

def calculate_agis(row):
    """
    Calcula a métrica AGIS para um jogador.
    
    AGIS = (PTS×1.0 + AST×1.8 + REB×1.2 + STL×2.5 + BLK×2.5 + EFF×0.7) × [1 + ((win_rate_do_oponente - 0.5) × 0.4)]
    """
    base_score = (
        row['PTS'] * 1.0 +
        row['AST'] * 1.8 +
        row['REB'] * 1.2 +
        row['STL'] * 2.5 +
        row['BLK'] * 2.5 +
        row['EFF'] * 0.7
    )
    
    opp_win_rate = row['OPP_WL_RATIO']
    win_rate_multiplier = 1 + ((opp_win_rate - 0.5) * 0.4)
    
    return base_score * win_rate_multiplier

try:
    season_type = "Playoffs"  # Definido como Playoffs por padrão
    print(f"\nAnalisando jogos da {season_type}...")
    
    print("Obtendo logs de jogos dos jogadores...")
    games_df = playergamelogs.PlayerGameLogs(
        season_nullable = '2024-25',  # Temporada atual
        season_type_nullable=season_type,
        date_from_nullable = "05/26/2025",                                                     
        date_to_nullable = "05/26/2025"
    ).player_game_logs.get_data_frame()

    print("Calculando métricas de eficiência...")
    games_df['EFF'] = (games_df['PTS'] + 
                      games_df['REB'] + 
                      games_df['AST'] + 
                      games_df['STL'] + 
                      games_df['BLK'] - 
                      (games_df['TOV'] + 
                       (games_df['FGA'] - games_df['FGM']) + 
                       (games_df['FTA'] - games_df['FTM'])))

    print("Extraindo informações da equipe oponente...")
    games_df['OPP_TEAM'] = games_df['MATCHUP'].apply(
        lambda x: x.split(' ')[-1] if '@' in x else x.split(' ')[0]
    )

    unique_opp_teams = games_df['OPP_TEAM'].unique()
    
    print(f"Obtendo registros para {len(unique_opp_teams)} equipes oponentes...")
    for team_abbr in unique_opp_teams:
        team_name = get_full_team_name(team_abbr)
        get_team_record(team_name, '2024-25', season_type)
        time.sleep(1)
    
    games_df['OPP_RECORD'] = games_df['OPP_TEAM'].apply(
        lambda x: team_record_cache.get(f"{get_full_team_name(x)}_2024-25_{season_type}", ("N/A", 0.0))[0]
    )
    
    games_df['OPP_WL_RATIO'] = games_df['OPP_TEAM'].apply(
        lambda x: team_record_cache.get(f"{get_full_team_name(x)}_2024-25_{season_type}", ("N/A", 0.0))[1]
    )
    
    print("Calculando métrica AGIS...")
    games_df['AGIS'] = games_df.apply(calculate_agis, axis=1)

    # Seleciona e ordena as colunas relevantes
    result_df = games_df[['PLAYER_NAME',
                         'MATCHUP',
                         'OPP_RECORD',
                         'PTS',
                         'REB',
                         'AST',
                         'STL',
                         'BLK',
                         'EFF',
                         'AGIS']].sort_values(by='AGIS', ascending=False)

    # Formata o DataFrame para melhor visualização
    pd.set_option('display.float_format', lambda x: '%.2f' % x)
    
    print(f"\nTop 10 jogadores por métrica AGIS ({season_type}):")
    print("=" * 100)
    print(result_df.head(10).to_string(index=False))
    print("=" * 100)

except Exception as e:
    print(f"Ocorreu um erro: {str(e)}") 