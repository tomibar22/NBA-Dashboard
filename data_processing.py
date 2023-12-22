import pandas as pd
from datetime import date
from nba_api.stats.endpoints import leaguegamelog, boxscoretraditionalv2, playbyplayv2, teamgamelog, leaguedashplayerstats, playergamelog, leaguedashteamstats
import streamlit as st

def sorted_df(df, stat, slider):
    current_columns = df.columns.tolist()
    percentage_columns = ['FG_PCT', 'FG3_PCT', 'FT_PCT', 'EFG_PCT']
    df[percentage_columns] = (df[percentage_columns] * 100).round(0).astype(int).astype(str) + '%'

    pct_col_dict = {
        'FG_PCT': [stat, 'FGM', 'FGA'],
        'FG3_PCT': [stat, 'FG3M', 'FG3A'],
        'FT_PCT': [stat, 'FTM', 'FTA'],
        'EFG_PCT': [stat, 'FGM', 'FGA']
    }

    if stat in pct_col_dict:
        df = df[df[pct_col_dict[stat][2]] >= slider].dropna() \
                                            .drop_duplicates() \
                                            .reset_index(drop=True)
        df = df.sort_values(stat, ascending=False)
 

        columns_to_move = pct_col_dict[stat]
        
        for col in columns_to_move:
            current_columns.remove(col)

        for col in reversed(columns_to_move):
            current_columns.insert(2, col)

        df = df[current_columns]

    else:
        df = df.dropna() \
                                    .drop_duplicates() \
                                    .sort_values(stat, ascending=False) \
                                    .reset_index(drop=True)
        current_columns.remove(stat)
        current_columns.insert(2, stat)
        df = df[current_columns]

    df = df.reset_index(drop=True)
    df.index = df.index + 1

    return df




def get_current_nba_season():
    today = date.today()
    if today.month >= 10:
        return f"{today.year}-{(today.year + 1) % 100:02d}"
    else:
        return f"{today.year - 1}-{today.year % 100:02d}"
current_season = get_current_nba_season()






def get_player_stats_per_game(season, season_type):
    players_df = leaguedashplayerstats.LeagueDashPlayerStats(per_mode_detailed='PerGame', season=season, season_type_all_star=season_type).get_data_frames()[0]
    players_df = players_df[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'PTS', 'AST', 'REB', 'OREB', 'DREB', 'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 'BLK', 'STL', 'TOV', 'PF', 'PLUS_MINUS', 'FT_PCT', 'FTM', 'FTA', 'MIN',  'AGE']]
    players_df = players_df.rename(columns={'TEAM_ABBREVIATION': 'TEAM',
                                        'PLAYER_NAME': 'PLAYER'})
    condition = players_df['FGA'] >= 10
    players_df.loc[condition, 'EFG_PCT'] = (players_df.loc[condition, 'FGM'] + (0.5 * players_df.loc[condition, 'FG3M'])) / players_df.loc[condition, 'FGA']
    players_df = players_df.dropna(subset='EFG_PCT')
    return players_df





def get_rookie_stats_per_game(season_type):
    rookie_df = leaguedashplayerstats.LeagueDashPlayerStats(per_mode_detailed='PerGame', player_experience_nullable='Rookie', season_type_all_star=season_type).get_data_frames()[0]
    rookie_df = rookie_df[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'PTS', 'AST', 'REB', 'OREB', 'DREB', 'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 'BLK', 'STL', 'TOV', 'PF', 'PLUS_MINUS', 'FT_PCT', 'FTM', 'FTA', 'MIN',  'AGE']]
    rookie_df = rookie_df.rename(columns={'TEAM_ABBREVIATION': 'TEAM',
                                        'PLAYER_NAME': 'PLAYER'})
    condition = rookie_df['FGA'] >= 5
    rookie_df.loc[condition, 'EFG_PCT'] = (rookie_df.loc[condition, 'FGM'] + (0.5 * rookie_df.loc[condition, 'FG3M'])) / rookie_df.loc[condition, 'FGA']
    rookie_df = rookie_df.dropna(subset='EFG_PCT')
    return rookie_df


def get_team_stats_per_game(season, season_type):
    teams_df = leaguedashteamstats.LeagueDashTeamStats(per_mode_detailed='PerGame', season=season, season_type_all_star=season_type).get_data_frames()[0]
    teams_df['WL'] = teams_df['W'].astype(str) + '-' + teams_df['L'].astype(str)
    teams_df = teams_df.drop(columns=['W', 'L'])
    teams_df = teams_df[['TEAM_NAME', 'WL', 'W_PCT', 'PTS', 'AST', 'REB', 'OREB', 'DREB', 'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 'BLK', 'STL', 'TOV', 'PF', 'PLUS_MINUS', 'FT_PCT', 'FTM', 'FTA']]
    teams_df = teams_df.rename(columns={'TEAM_NAME': 'TEAM'})
    condition = teams_df['FGA'] >= 10
    teams_df.loc[condition, 'EFG_PCT'] = (teams_df.loc[condition, 'FGM'] + (0.5 * teams_df.loc[condition, 'FG3M'])) / teams_df.loc[condition, 'FGA']
    return teams_df



def get_player_games(player_id, season, season_type, stat):
    player_games = playergamelog.PlayerGameLog(player_id=player_id, season=season, season_type_all_star=season_type).get_data_frames()[0]
    player_games = player_games.drop(columns=['SEASON_ID', 'Player_ID', 'Game_ID', 'VIDEO_AVAILABLE'])
    player_games = player_games[['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'AST', 'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 
                                'REB', 'OREB', 'DREB', 'BLK', 'STL', 'TOV', 'PF', 'PLUS_MINUS', 'FT_PCT', 'FTM', 'FTA', 'MIN']]
    columns_to_convert = ['PTS', 'AST', 'REB', 'FGM', 'FGA', 'FG3M', 'FG3A', 'BLK', 'STL', 'PLUS_MINUS', 'FTM', 'FTA', 'PF', 'MIN']
    player_games[columns_to_convert] = player_games[columns_to_convert].astype(int)
    condition = player_games['FGA'] >= 10
    player_games.loc[condition, 'EFG_PCT'] = (player_games.loc[condition, 'FGM'] + (0.5 * player_games.loc[condition, 'FG3M'])) / player_games.loc[condition, 'FGA']
    player_games[['FG_PCT_CLEAN', 'FG3_PCT_CLEAN', 'FT_PCT_CLEAN', 'EFG_PCT_CLEAN']] = player_games[['FG_PCT', 'FG3_PCT', 'FT_PCT', 'EFG_PCT']]
    player_games[['FG_PCT_CLEAN', 'FG3_PCT_CLEAN', 'FT_PCT_CLEAN', 'EFG_PCT_CLEAN']] = player_games[['FG_PCT_CLEAN', 'FG3_PCT_CLEAN', 'FT_PCT_CLEAN', 'EFG_PCT']].apply(pd.to_numeric, errors='coerce')
    percentage_columns = ['FG_PCT', 'FG3_PCT', 'FT_PCT',  'EFG_PCT']
    player_games[percentage_columns] = (player_games[percentage_columns] * 100).round(0).astype(int).astype(str) + '%'

    if stat:
        columns_to_move_mapping = {
        'FG_PCT': [stat, 'FGM', 'FGA'],
        'FG3_PCT': [stat, 'FG3M', 'FG3A'],
        'FT_PCT': [stat, 'FTM', 'FTA']
         }
        current_columns = player_games.columns.tolist()
        new_position = 3
        if stat in columns_to_move_mapping:
            columns_to_move = columns_to_move_mapping[stat]

            for col in columns_to_move:
                current_columns.remove(col)

            for col in reversed(columns_to_move):
                current_columns.insert(new_position, col)

            player_games = player_games[current_columns].set_index(player_games.columns[0])

        else:
            current_columns.remove(stat)
            current_columns.insert(new_position, stat)
            player_games = player_games[current_columns].set_index(player_games.columns[0])
    
    return player_games
