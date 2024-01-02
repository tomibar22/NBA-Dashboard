import pandas as pd
from datetime import datetime, timedelta
from nba_api.stats.endpoints import leaguegamelog, boxscoretraditionalv2, playbyplayv2, teamgamelog
import streamlit as st
import plotly.express as px

from data_processing import sorted_df
from st_pages import Page, show_pages, add_page_title

show_pages(
    [
        Page('home.py', "Yesterday's Games"),
        Page('pages/Standings (Desktop).py'),
        Page('pages/Standings (Mobile).py'),
        Page('pages/News.py'),
        Page('pages/Player Stats.py'),
        Page('pages/Team Stats.py'),
        Page('pages/Stats Per Game (Players).py'),
        Page('pages/Stats Per Game (Teams).py')
    ]
)
st.set_page_config(page_title="Yesterday's Games",
                   layout="wide")




@st.cache_data(ttl=timedelta(hours=1))
def get_yesterday_games_ids():
    games_df = leaguegamelog.LeagueGameLog().get_data_frames()[0]
    games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE'])
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_date = yesterday.date()
    yesterday_games_df = games_df[games_df['GAME_DATE'].dt.date == yesterday_date]
    yesterday_games_ids = list(yesterday_games_df['GAME_ID'].unique())
    yesterday_teams_ids = list(yesterday_games_df['TEAM_ID'].unique())
    yesterday_team_names = list(yesterday_games_df['TEAM_ABBREVIATION'].unique())
    return yesterday_games_ids, yesterday_teams_ids, yesterday_team_names




@st.cache_data(ttl=timedelta(hours=1))
def get_yesterday_clutch_games():
    processed_game_ids = set()
    clutch_games_summary = {}
    
    for game_id in get_yesterday_games_ids()[0]:
        if game_id in processed_game_ids:
            continue

        play_by_play_df = playbyplayv2.PlayByPlayV2(game_id=game_id).get_data_frames()[0]
        fourth_period_plays = play_by_play_df[play_by_play_df['PERIOD'] == 4].copy()

        fourth_period_plays['NEWTIMESTRING'] = fourth_period_plays['PCTIMESTRING'].apply(
            lambda x: sum(int(i) * 60 ** j for j, i in enumerate(reversed(x.split(':'))))
        )

        max_time = fourth_period_plays['NEWTIMESTRING'].max()
        fourth_period_plays['TIME_DIFF'] = max_time - fourth_period_plays['NEWTIMESTRING']

        last_five_minutes_plays = fourth_period_plays[
            (fourth_period_plays['EVENTMSGTYPE'].isin([1, 2, 3])) &  # Include only made field goals, free throws, or 3-pointers
            (fourth_period_plays['TIME_DIFF'] >= 420) &
            (fourth_period_plays['TIME_DIFF'] <= 720)
        ]

        last_five_minutes_plays = last_five_minutes_plays.replace("None", pd.NA)
        last_five_minutes_plays['SCOREMARGIN'] = pd.to_numeric(last_five_minutes_plays['SCOREMARGIN'], errors='coerce')
        last_five_minutes_plays = last_five_minutes_plays.dropna(subset=['SCOREMARGIN'])
        last_five_minutes_plays = last_five_minutes_plays[
            (last_five_minutes_plays['SCOREMARGIN'] >= -10) & (last_five_minutes_plays['SCOREMARGIN'] <= 10)
        ]

        if not last_five_minutes_plays.empty:
            clutch_margin_sum = abs(last_five_minutes_plays['SCOREMARGIN'].mean())
            clutch_games_summary[game_id] = clutch_margin_sum

        processed_game_ids.add(game_id)

    # Sort games by total clutch margin
    sorted_clutch_games = sorted(clutch_games_summary.items(), key=lambda x: x[1])

    yesterday_clutch_games = [
        {
            'matchup': f"{teams[0]} vs {teams[1]}",
            'clutch_margin_avg': round(float(clutch_margin), 2)
        }
        for clutch_game_id, clutch_margin in sorted_clutch_games
        for teams in [list(boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=clutch_game_id).get_data_frames()[0]['TEAM_ABBREVIATION'].unique())]
    ]

    return yesterday_clutch_games











@st.cache_data(ttl=timedelta(hours=1))
def get_yesterday_stats():
    yesterday_games = get_yesterday_games_ids()[0]
    yesterday_stats = []

    for game_id in yesterday_games:
        boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id).get_data_frames()[0]
        stats = boxscore[['TEAM_ABBREVIATION', 'PLAYER_NAME', 'PTS', 'AST', 'REB', 'OREB', 'DREB', 'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 'BLK', 'STL', 'PF', 'PLUS_MINUS', 'FT_PCT', 'FTM', 'FTA', 'MIN']]
        stats = stats.dropna(subset='MIN')
        stats['MIN'] = stats['MIN'].apply(lambda x: int(x.split('.')[0]))
        condition = stats['FGA'] >= 10
        stats.loc[condition, 'TS_PCT'] = stats.loc[condition, 'PTS'] / (2 * (stats.loc[condition, 'FGA'] + 0.44 * stats.loc[condition, 'FTA']))
        stats = stats.dropna(subset='TS_PCT')
        stats = stats.rename(columns={'TEAM_ABBREVIATION': 'TEAM',
                                      'PLAYER_NAME': 'PLAYER'})
        yesterday_stats.append(stats)

    yesterday_stats = pd.concat(yesterday_stats, ignore_index=True)
    return yesterday_stats








@st.cache_data(ttl=timedelta(hours=1))
def get_team_stats():
    game_ids, team_ids, team_names = get_yesterday_games_ids()

    team_stats_dfs = []
    for team_id in team_ids:
        team_stats = teamgamelog.TeamGameLog(team_id=team_id).get_data_frames()[0]
        team_stats_dfs.append(team_stats)

    team_stats = pd.concat(team_stats_dfs, ignore_index=True)
    team_stats = team_stats[team_stats['Game_ID'].isin(game_ids)]
    team_stats = team_stats.drop(columns=['Game_ID', 'GAME_DATE', 'Team_ID', 'MIN'])
    team_stats['TEAM'] = team_names
    team_stats['MATCHUP'] = team_stats['MATCHUP'].str.extract(r'(vs\. \w+|@ \w+)')
    columns_to_convert = ['PTS', 'AST', 'REB', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB', 'BLK', 'STL']
    team_stats[columns_to_convert] = team_stats[columns_to_convert].astype(int)
    condition = team_stats['FGA'] >= 10
    team_stats.loc[condition, 'TS_PCT'] = (team_stats.loc[condition, 'FGM'] + (0.5 * team_stats.loc[condition, 'FG3M'])) / team_stats.loc[condition, 'FGA']
    percentage_columns = ['FG_PCT', 'FG3_PCT', 'FT_PCT', 'W_PCT', 'TS_PCT']
    team_stats[percentage_columns] = (team_stats[percentage_columns] * 100).round(0).astype(int).astype(str) + '%'
    team_stats = team_stats[['TEAM', 'MATCHUP', 'PTS', 'AST', 'TS_PCT', 'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 
                             'REB', 'OREB', 'DREB', 'BLK', 'STL', 'TOV', 'PF', 'FT_PCT', 'FTM', 'FTA', 'WL', 'W','L', 'W_PCT']]
    return team_stats







def team_stats_leaders(stat):
    pct_col_dict = {
        'FG_PCT': [stat, 'FGM', 'FGA'],
        'FG3_PCT': [stat, 'FG3M', 'FG3A'],
        'FT_PCT': [stat, 'FTM', 'FTA'],
        'TS_PCT': [stat, 'FGM', 'FGA']
    }
    if stat in pct_col_dict:
        team_stats_leaders = get_team_stats().dropna() \
                                        .sort_values(stat, ascending=False) \
                                        .reset_index(drop=True)
    else:
        team_stats_leaders = get_team_stats().dropna() \
                                            .sort_values(stat, ascending=False) \
                                            .reset_index(drop=True)
    
    current_columns = team_stats_leaders.columns.tolist()
    new_position = 2


    if stat in pct_col_dict:
        columns_to_move = pct_col_dict[stat]

        for col in columns_to_move:
            current_columns.remove(col)

        for col in reversed(columns_to_move):
            current_columns.insert(new_position, col)

        team_stats_leaders = team_stats_leaders[current_columns]

    else:
        current_columns.remove(stat)
        current_columns.insert(new_position, stat)
        team_stats_leaders = team_stats_leaders[current_columns]


    return team_stats_leaders









clutch_games_list = get_yesterday_clutch_games()

if clutch_games_list:
    with st.container(border=True):
        st.markdown("<h2 style='text-align: center; letter-spacing: 4px; word-spacing: 20px; font-size: 50px;'>Yesterday's Clutch Games:</h2>", unsafe_allow_html=True)
        st.markdown('')
        for game in clutch_games_list:
            matchup = game['matchup']
            clutch_margin_avg = game['clutch_margin_avg']

            st.markdown(f"<h1 style='text-align: center; letter-spacing: 5px; word-spacing: 12px; font-size: 60px;'><big>{matchup}</big></h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; letter-spacing: 2px; font-size: 20px;'>Clutch Margin Avg: <b>{clutch_margin_avg}</b></p>", unsafe_allow_html=True)
            st.markdown('')
        st.markdown('')
        


    st.markdown("#")

else:
    st.warning("No clutch games to display.")


try:
    col1, col2, col3 = st.columns([1,4,1])

    yesterday_stats = get_yesterday_stats()
    


    with col2:
        with st.expander("Player Stats"):
            player_stat = st.selectbox('Sort By:',['PTS', 'TS_PCT', 'AST', 'REB', 'OREB', 'DREB', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 
                                                   'BLK', 'STL', 'PLUS_MINUS', 'PF', 'FT_PCT', 'MIN'], label_visibility='hidden')

            pct =  {
                'FG_PCT': [player_stat, 'FGM', 'FGA'],
                'FG3_PCT': [player_stat, 'FG3M', 'FG3A'],
                'FT_PCT': [player_stat, 'FTM', 'FTA'],
                'TS_PCT': [player_stat, 'FGM', 'FGA']
                }
            
            if 'PCT' in player_stat:
                min_value = yesterday_stats[yesterday_stats[pct[player_stat][2]] > 0][pct[player_stat][2]].min()
                max_value = yesterday_stats[pct[player_stat][2]].max()
                slider = st.slider('Minimum Attempts', min_value, max_value, value=max_value / 2, step=1.0, format='%d')
            else:
                slider = None
            players_df = sorted_df(yesterday_stats, player_stat, slider)


            players_df = players_df.head(25)
            
            if 'PCT' in player_stat:
                players_df[player_stat] = players_df[player_stat].str.rstrip('%').astype('int') / 100.0

            fig = px.bar(players_df.head(10), x='PLAYER', y=player_stat,
                        text=player_stat,
                        hover_data= pct[player_stat] if 'PCT' in player_stat else None,
                        color=player_stat,
                        color_continuous_midpoint=players_df[player_stat].mean(),
                        color_continuous_scale='Blues')

            if 'PCT' in player_stat:
                fig.update_traces(texttemplate='%{text:.0%}'+'<br>%{customdata[0]}/%{customdata[1]}', textposition='inside',
                                    hovertemplate='%{x}'+'<br>%{text:.0%}'+'<br>%{customdata[0]}/%{customdata[1]}')
            else:
                fig.update_traces(texttemplate='%{text}', textposition='inside',
                                    hovertemplate='%{x}'+'<br>%{text}'+f' {player_stat}')
            fig.update_layout(coloraxis_showscale=False,
                            xaxis=dict(title_text='', tickfont=dict(size=20)),
                            yaxis=dict(title_text='', tickfont=dict(size=20)),
                            font=dict(size=20),
                            hoverlabel=dict(font_size=20),
                            height=600)
            st.plotly_chart(fig, use_container_width=True)
            players_df = players_df.set_index(players_df.columns[0])
            if 'PCT' in player_stat:
                # Convert percentage columns to numeric and format as percentage
                players_df[player_stat] = pd.to_numeric(players_df[player_stat], errors='coerce')
                players_df[player_stat] = players_df[player_stat].map(lambda x: f'{x:.0%}' if pd.notnull(x) else '')

            # Display the DataFrame in Streamlit
            st.dataframe(players_df, width=1500)

    col1, col2, col3 = st.columns([1,4,1])
    with col2:
        with st.expander("Team Stats"):
            team_stat = st.selectbox('Sort By:', ['PTS', 'TS_PCT', 'AST', 'REB', 'OREB', 'DREB', 'FG_PCT', 'FG3_PCT', 'BLK', 'STL', 'TOV', 'PF', 'FT_PCT'], label_visibility='hidden')
            team_df = team_stats_leaders(team_stat)
            pct = {
                'FG_PCT': [team_stat, 'FGM', 'FGA', 'WL'],
                'FG3_PCT': [team_stat, 'FG3M', 'FG3A', 'WL'],
                'FT_PCT': [team_stat, 'FTM', 'FTA', 'WL'],
                'TS_PCT': [team_stat, 'FGM', 'FGA', 'WL']
            }
            if '100%' in team_df[team_stat].unique():
                team_df = team_df.loc[team_df[team_stat] != '100%']

            if 'PCT' in team_stat:
                team_df[team_stat] = team_df[team_stat].str.rstrip('%').astype('float') / 100.0


            fig = px.bar(team_df.head(10), x='TEAM', y=team_stat,
                        text=team_stat,
                        hover_data=pct[team_stat] if 'PCT' in team_stat else ['WL'],
                        color=team_stat,
                        color_continuous_midpoint=team_df[team_stat].mean(),
                        color_continuous_scale='Greens')

            if 'PCT' in team_stat:
                fig.update_traces(texttemplate='%{text:.0%}'+'<br>%{customdata[0]}/%{customdata[1]}', textposition='inside',
                                    hovertemplate='%{x}'+'<br>%{text:.0%}'+'<br>%{customdata[0]} / %{customdata[1]}' + '<br>%{customdata[2]}')
            else:
                fig.update_traces(texttemplate='%{text}', textposition='inside',
                                    hovertemplate='%{x}'+'<br>%{text}'+f' {team_stat}' + '<br>%{customdata[0]}')

            fig.update_layout(coloraxis_showscale=False,
                            xaxis=dict(title_text='', tickfont=dict(size=20)),
                            yaxis=dict(title_text='', tickfont=dict(size=20)),
                            font=dict(size=20),
                            hoverlabel=dict(font_size=20),
                            height=600)

            st.plotly_chart(fig, use_container_width=True)
            team_df = team_df.set_index(team_df.columns[0])
            st.dataframe(team_df.style.format({team_stat: "{:.0%}"}) if 'PCT' in team_stat else team_df, width=1500)
except Exception as e:
    print(f"An error occurred: {e}")
    
