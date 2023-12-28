import pandas as pd
from datetime import date
from nba_api.stats.endpoints import leaguegamelog, boxscoretraditionalv2, playbyplayv2, teamgamelog, playergamelog, commonplayerinfo
from nba_api.stats.static import players
import streamlit as st
import streamlit_antd_components as sac
import plotly.express as px
import plotly.graph_objects as go

from data_processing import get_current_nba_season, get_player_stats_per_game, sorted_df, get_player_games


st.set_page_config(page_title="Player Stats Browser",
                   layout="wide")

active_players_df = pd.DataFrame(players.get_active_players())
inactive_players_df = pd.DataFrame(players.get_inactive_players())
all_players_df = pd.concat([active_players_df, inactive_players_df], ignore_index=True)
player_names_ids = dict(zip(all_players_df['full_name'], all_players_df['id']))
player_names = player_names_ids.keys()
   
current_season = get_current_nba_season()

def search_player_names(search_term: str) -> list[any]:
    search_term_lower = search_term.lower()

    matching_names = [player_name for player_name in player_names
                    if search_term_lower in player_name.lower()]

    return matching_names


best_players = get_player_stats_per_game(current_season, 'Regular Season')    
number_of_buttons = 60
best_players = sorted_df(best_players,'PTS', slider=None).head(number_of_buttons)
best_players = best_players['PLAYER']
chip_items = [sac.ChipItem(label=player) for player in best_players]
extra_chip = sac.ChipItem(label='Other', icon='search')
chip_items.append(extra_chip)
chip = sac.chip(items=chip_items, align='center', size='md', radius='xl', multiple=False, index=[number_of_buttons], key='chips')

if chip == 'Other':
    c1, c2, c3= st.columns([4,3,4])
    with c2:
        search = st.selectbox('Search',list(player_names_ids.keys()), index=None, placeholder='Search a player...', label_visibility='hidden')            
        # st.markdown("<p style='padding-top:13.5px;'></p>", unsafe_allow_html=True)
        # search = st_searchbox(search_player_names, disabled=True)
        player = search
        if player:
            st.markdown(f"<h2 style='text-align: center; letter-spacing: 4px; word-spacing: 20px; font-size: 50px;'>{player}</h2>", unsafe_allow_html=True)
else:
    player = chip
    c1, c2, c3= st.columns([4,6,4])
    with c2:
        st.markdown(f"<h2 style='text-align: center; letter-spacing: 4px; word-spacing: 20px; font-size: 50px;'>{player}</h2>", unsafe_allow_html=True)

player_id = player_names_ids.get(player)


try:
    c1,c2,c3,c4 = st.columns([4,3,3,4])
    with c2:
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id).get_data_frames()[0]
        start_year = int(player_info['FROM_YEAR'].iloc[0])
        end_year = int(player_info['TO_YEAR'].iloc[0])
        nba_seasons = [f"{year}-{(year + 1) % 100:02d}" for year in range(start_year, end_year + 1)]
        season = st.selectbox('Season', nba_seasons[::-1], index=0, label_visibility='hidden')

    with c3:
        season_type = st.selectbox('Season Type', ['Regular Season', 'Playoffs'], label_visibility='hidden')
except:
    with c2:
        season = st.selectbox('Season',[current_season], disabled=True, label_visibility='hidden')
    with c3:
        season_type = st.selectbox('Season_Type', ['Regular Season', 'Playoffs'], label_visibility='hidden')


try:

    player_games=get_player_games(player_id, season, season_type, stat=None)
    st.markdown('')



    with st.container(border=True):
            cl1, cl2, cl3, cl4, cl5, cl6, cl7, cl8, cl9, cl10, cl11, cl12, cl13 = st.columns(13)
            font_size = "style='font-size: 22px'"
            cl1.markdown(f"<p style='text-align: center;'>PTS<br><b {font_size}>{(player_games['PTS'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
            cl2.markdown(f"<p style='text-align: center;'>EFG_PCT</b><br><b {font_size}>{(player_games['EFG_PCT_CLEAN'].mean()*100).round(1)}%</b></p>", unsafe_allow_html=True)
            cl3.markdown(f"<p style='text-align: center;'>AST<br><b {font_size}>{(player_games['AST'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
            cl4.markdown(f"<p style='text-align: center;'>REB</b><br><b {font_size}>{(player_games['REB'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
            cl5.markdown(f"<p style='text-align: center;'>FG_PCT<br><b {font_size}>{(player_games['FG_PCT_CLEAN'].mean()*100).round(1)}%</b></p>", unsafe_allow_html=True)
            cl6.markdown(f"<p style='text-align: center;'>FG3_PCT<br><b {font_size}>{(player_games['FG3_PCT_CLEAN'].mean()*100).round(1)}%</b></p>", unsafe_allow_html=True)
            cl7.markdown(f"<p style='text-align: center;'>BLK<br><b {font_size}>{(player_games['BLK'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
            cl8.markdown(f"<p style='text-align: center;'>STL<br><b {font_size}>{(player_games['STL'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
            cl9.markdown(f"<p style='text-align: center;'>TOV<br><b {font_size}>{(player_games['TOV'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
            cl10.markdown(f"<p style='text-align: center;'>PF<br><b {font_size}>{(player_games['PF'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
            cl11.markdown(f"<p style='text-align: center;'>PLUS_MINUS<br><b {font_size}>{(player_games['PLUS_MINUS'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
            cl12.markdown(f"<p style='text-align: center;'>FT_PCT<br><b {font_size}>{(player_games['FT_PCT_CLEAN'].mean()*100).round(1)}%</b></p>", unsafe_allow_html=True)
            cl13.markdown(f"<p style='text-align: center;'>MIN<br><b {font_size}>{(player_games['MIN'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
except:
    pass

cl1, cl2, cl3 = st.columns([4,3,4])
with cl2:
    if player:
        stat = st.selectbox('Stat', ['PTS', 'EFG_PCT', 'AST', 'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 
                                'REB', 'OREB', 'DREB', 'BLK', 'STL', 'TOV', 'PF', 'PLUS_MINUS', 'FT_PCT', 'FTM', 'FTA', 'MIN'], label_visibility='hidden')


try:
    player_games = get_player_games(player_id, season, season_type, stat)
    
    pct = {
        'FG_PCT': [stat, 'FGM', 'FGA', 'WL'],
        'FG3_PCT': [stat, 'FG3M', 'FG3A', 'WL'],
        'FT_PCT': [stat, 'FTM', 'FTA', 'WL'],
        'EFG_PCT': [stat, 'FGM', 'FGA', 'WL']
            }

    fig = px.line(player_games, x=player_games.index, y=stat, markers=True, 
                  hover_data=pct[stat] if 'PCT' in stat else ['WL'],
                  text=stat)
    if 'PCT' in stat:
        y_max = player_games[f'{stat}_CLEAN'].max() *100 +10
        if 'FT_PCT' in stat:
            player_games = player_games[player_games['FT_PCT'] != 0]
    else:
        y_max = None
    fig.update_layout(xaxis=dict(autorange="reversed", title_text='', tickfont=dict(size=17)),
                      yaxis=dict(title_text='', tickfont=dict(size=16), range=[0,y_max]),
                      height=800)
    
    fig.update_xaxes(ticktext=player_games["MATCHUP"].str.extract(r'(vs\. \w+|@ \w+)'), tickvals=player_games.index)

    fig.update_traces(
                    textposition='top center',
                    textfont_size=19,
                    marker=dict(size=8,
                                color='#ECF0F1'),
                    line=dict(color='#2471A3',
                            width=5),
                    # fill='tozeroy',
                    line_shape='spline')

    if 'PCT' in stat:
        fig.update_traces(texttemplate='%{y}%'+'<br>%{customdata[0]}/%{customdata[1]}', hovertemplate='<br>%{text}' + '<br>%{x}' +  '<br>%{y}% '+'<br>%{customdata[0]}/%{customdata[1]}' + '<br>%{customdata[2]}', 
                          text=player_games.index)
    else:
        fig.update_traces(texttemplate='%{y}', hovertemplate='<br>%{text}' + '<br>%{x}' +  '<br>%{y} ' + f'{stat}' + '<br>%{customdata[0]}', text=player_games.index)

    for x_value, y_value in zip(player_games.index, player_games[stat]):
        fig.add_trace(go.Scatter(x=[x_value, x_value], y=[0, y_value],
                                mode='lines',
                                line=dict(color='#D5DBDB', width=0.5, dash='dash'),
                                showlegend=False))
    st.plotly_chart(fig, use_container_width=True)

    cl1, cl2, cl3 = st.columns([1,5,1])
    with cl2:
        player_games = player_games.drop(columns=['FG_PCT_CLEAN', 'FG3_PCT_CLEAN', 'FT_PCT_CLEAN', 'EFG_PCT_CLEAN'])
        st.markdown('')
        with st.expander('Show Full Data'):
            st.dataframe(player_games, use_container_width=True)

except:
    pass
