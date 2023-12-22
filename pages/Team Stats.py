import pandas as pd
from datetime import date
from nba_api.stats.endpoints import leaguegamelog, boxscoretraditionalv2, playbyplayv2, teamgamelog, playergamelog, commonplayerinfo
from nba_api.stats.static import teams
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import streamlit_antd_components as sac
from data_processing import get_current_nba_season
st.set_page_config(layout="wide")

# st.session_state
# if "stat" not in st.session_state:
#     st.session_state.stat = 'PTS'

# if "pts" not in st.session_state:
#     st.session_state.pts = 'color:#138D75;'

# if "ast" not in st.session_state:
#     st.session_state.ast = ''

# # if "pts" not in st.session_state:
# #     st.session_state.pts = ''

# # if "pts" not in st.session_state:
# #     st.session_state.pts = ''

# # if "pts" not in st.session_state:
# #     st.session_state.pts = ''




teams_df = pd.DataFrame(teams.get_teams())
c1,c2,c3 = st.columns([4,6,4])
with c2:
    with st.container(border=False):
        
        team = st.selectbox('Team', teams_df['full_name'], index=None, key='selectbox', label_visibility='hidden')

team_id = teams_df[teams_df['full_name']==team]['id']

current_season = get_current_nba_season()
c1, c2, c3, c4= st.columns([4,3,3,4])
with c2:
    nba_seasons = [f"{year}-{(year + 1) % 100:02d}" for year in range(1960, int(current_season.split('-')[0]) + 1)]
    season = st.selectbox('Season', nba_seasons[::-1], index=0, label_visibility='hidden')

with c3:
    season_type = st.selectbox('Season Type', ['Regular Season', 'Playoffs'], label_visibility='hidden')


def get_team_games(stat):
    team_games = teamgamelog.TeamGameLog(team_id=team_id, season=season, season_type_all_star=season_type).get_data_frames()[0]
    team_games = team_games.drop(columns=['Team_ID', 'Game_ID'])
    team_games = team_games[['GAME_DATE', 'MATCHUP', 'PTS', 'AST', 'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 
                                'REB', 'OREB', 'DREB', 'BLK', 'STL', 'TOV', 'PF', 'FT_PCT', 'FTM', 'FTA', 'WL', 'W', 'L', 'W_PCT']]
    columns_to_convert = ['PTS', 'AST', 'REB', 'FGM', 'FGA', 'FG3M', 'FG3A', 'BLK', 'STL','FTM', 'FTA', 'PF', 'W', 'L']
    team_games[columns_to_convert] = team_games[columns_to_convert].astype(int)
    condition = team_games['FGA'] >= 10
    team_games.loc[condition, 'EFG_PCT'] = (team_games.loc[condition, 'FGM'] + (0.5 * team_games.loc[condition, 'FG3M'])) / team_games.loc[condition, 'FGA']
    team_games[['FG_PCT_CLEAN', 'FG3_PCT_CLEAN', 'FT_PCT_CLEAN', 'W_PCT_CLEAN', 'EFG_PCT_CLEAN']] = team_games[['FG_PCT', 'FG3_PCT', 'FT_PCT', 'W_PCT', 'EFG_PCT']]
    team_games[['FG_PCT_CLEAN', 'FG3_PCT_CLEAN', 'FT_PCT_CLEAN', 'W_PCT_CLEAN']] = team_games[['FG_PCT_CLEAN', 'FG3_PCT_CLEAN', 'FT_PCT_CLEAN', 'W_PCT_CLEAN']].apply(pd.to_numeric, errors='coerce')
    percentage_columns = ['FG_PCT', 'FG3_PCT', 'FT_PCT', 'W_PCT', 'EFG_PCT']
    team_games[percentage_columns] = (team_games[percentage_columns] * 100).round(0).astype(int).astype(str) + '%'
    if stat:
        columns_to_move_mapping = {
        'FG_PCT': [stat, 'FGM', 'FGA'],
        'FG3_PCT': [stat, 'FG3M', 'FG3A'],
        'FT_PCT': [stat, 'FTM', 'FTA'],
        'EFG_PCT': [stat, 'FGM', 'FGA']
         }
        current_columns = team_games.columns.tolist()
        new_position = 2
        if stat in columns_to_move_mapping:
            columns_to_move = columns_to_move_mapping[stat]

            for col in columns_to_move:
                current_columns.remove(col)

            for col in reversed(columns_to_move):
                current_columns.insert(new_position, col)

            team_games = team_games[current_columns].set_index(team_games.columns[0])

        else:
            current_columns.remove(stat)
            current_columns.insert(new_position, stat)
            team_games = team_games[current_columns].set_index(team_games.columns[0])
    
    return team_games

if team:
    st.markdown(f"<h2 style='text-align: center; letter-spacing: 4px; word-spacing: 20px; font-size: 50px;'>{team}</h2>", unsafe_allow_html=True)

try:
    
    team_games=get_team_games(stat=None) 


    # def stat_color():
    #     st.session_state.pts = ''
    #     st.session_state.ast = ''
    #     st.session_state.reb = ''
    #     st.session_state.fgpct = ''
    #     st.session_state.fg3pct = ''
    #     st.session_state.blk = ''
    #     st.session_state.stl = ''
    #     st.session_state.tov = ''
    #     st.session_state.pf = ''
    #     st.session_state.ftpct = ''
    #     if st.session_state.stat == 'PTS':
    #         st.session_state.pts = 'color: #138D75;'

    #     elif st.session_state.stat == 'AST':
    #         st.session_state.ast = 'color: #138D75;'

    #     elif st.session_state.stat == 'REB':
    #         st.session_state.reb = 'color: #138D75;'

    #     elif st.session_state.stat == 'FG_PCT':
    #         st.session_state.fgpct = 'color: #138D75;'

    #     elif st.session_state.stat == 'FG3_PCT':
    #         st.session_state.fg3pct = 'color: #138D75;'

    #     elif st.session_state.stat == 'BLK':
    #         st.session_state.blk = 'color: #138D75;'

    #     elif st.session_state.stat == 'STL':
    #         st.session_state.stl = 'color: #138D75;'

    #     elif st.session_state.stat == 'TOV':
    #         st.session_state.tov = 'color: #138D75;'

    #     elif st.session_state.stat == 'PF':
    #         st.session_state.pf = 'color: #138D75;'

    #     elif st.session_state.stat == 'FT_PCT':
    #         st.session_state.ftpct = 'color: #138D75;'
    #     else:
    #         pass


    st.markdown('')

    with st.container(border=True):
        cl1, cl2, cl3, cl4, cl5, cl6, cl7, cl8, cl9, cl10, cl11 = st.columns(11)
        font_size = "style='font-size: 22px'"
        color = 'color:#138D75'
        cl1.markdown(f"<p style='text-align: center;'>PTS<br><b {font_size}>{(team_games['PTS'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
        cl2.markdown(f"<p style='text-align: center;'>EFG_PCT<br><b {font_size}>{(team_games['EFG_PCT_CLEAN'].mean()*100).round(1)}%</b></p>", unsafe_allow_html=True)
        cl3.markdown(f"<p style='text-align: center;'>AST<br><b {font_size}>{(team_games['AST'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
        cl4.markdown(f"<p style='text-align: center;'>REB</b><br><b {font_size}>{(team_games['REB'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
        cl5.markdown(f"<p style='text-align: center;'>FG_PCT<br><b {font_size}>{(team_games['FG_PCT_CLEAN'].mean()*100).round(1)}%</b></p>", unsafe_allow_html=True)
        cl6.markdown(f"<p style='text-align: center;'>FG3_PCT<br><b {font_size}>{(team_games['FG3_PCT_CLEAN'].mean()*100).round(1)}%</b></p>", unsafe_allow_html=True)
        cl7.markdown(f"<p style='text-align: center;'>BLK<br><b {font_size}>{(team_games['BLK'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
        cl8.markdown(f"<p style='text-align: center;'>STL<br><b {font_size}>{(team_games['STL'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
        cl9.markdown(f"<p style='text-align: center;'>TOV<br><b {font_size}>{(team_games['TOV'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
        cl10.markdown(f"<p style='text-align: center;'>PF<br><b {font_size}>{(team_games['PF'].mean()).round(1)}</b></p>", unsafe_allow_html=True)
        cl11.markdown(f"<p style='text-align: center;'>FT_PCT<br><b {font_size}>{(team_games['FT_PCT_CLEAN'].mean()*100).round(1)}%</b></p>", unsafe_allow_html=True)

except:
    pass
if team:
    cl1, cl2, cl3 = st.columns([4,3,4])
    with cl2:
        stat = st.selectbox('Stat', ['PTS', 'EFG_PCT', 'AST', 'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 
                                    'REB', 'OREB', 'DREB', 'BLK', 'STL', 'TOV', 'PF', 'FT_PCT', 'FTM', 'FTA', 'WL'], label_visibility='hidden', index=0)



    try:
        team_games = get_team_games(stat)
        
        pct = {
            'FG_PCT': [stat, 'FGM', 'FGA'],
            'FG3_PCT': [stat, 'FG3M', 'FG3A'],
            'FT_PCT': [stat, 'FTM', 'FTA'],
            'EFG_PCT': [stat, 'FGM', 'FGA']
                }

        fig = px.line(team_games, x=team_games.index, y=stat, markers=True, 
                    hover_data=pct[stat] if 'PCT' in stat else None,
                    text=stat)
        if 'PCT' in stat:
            y_max = team_games[f'{stat}_CLEAN'].max() *100 +10
        else:
            y_max = None
        fig.update_layout(xaxis=dict(autorange="reversed", title_text='', tickfont=dict(size=17)),
                        yaxis=dict(title_text='', tickfont=dict(size=16), range=[0,y_max]),
                        height=600,
                        yaxis_categoryorder='category ascending')
        
        fig.update_xaxes(ticktext=team_games["MATCHUP"].str.extract(r'(vs\. \w+|@ \w+)'), tickvals=team_games.index)

        fig.update_traces(
                        textposition='top center',
                        textfont_size=19,
                        marker=dict(size=8,
                                    color='#ECF0F1'),
                        line=dict(color='#138D75',
                                width=5),
                        # fill='tozeroy',
                        line_shape='spline')
        if 'PCT' in stat:
            fig.update_traces(texttemplate='%{y}%'+'<br>%{customdata[0]}/%{customdata[1]}', hovertemplate='<br>%{text}' + '<br>%{x}' +  '<br>%{y}% '+'<br>%{customdata[0]}/%{customdata[1]}', 
                            text=team_games.index)
        elif stat == 'WL':
            fig.update_traces(texttemplate='%{y}', hovertemplate='<br>%{text}' + '<br>%{x}' +  '<br>%{y} ', text=team_games.index)

        else:
            fig.update_traces(texttemplate='%{y}', hovertemplate='<br>%{text}' + '<br>%{x}' +  '<br>%{y} ' + f'{stat}', text=team_games.index)

        for x_value, y_value in zip(team_games.index, team_games[stat]):
            fig.add_trace(go.Scatter(x=[x_value, x_value], y=[0, y_value],
                                mode='lines',
                                line=dict(color='#D5DBDB', width=1, dash='dash'),
                                showlegend=False))

        st.plotly_chart(fig, use_container_width=True)

        cl1, cl2, cl3 = st.columns([1,5,1])
        with cl2:
            team_games = team_games.drop(columns=['FG_PCT_CLEAN', 'FG3_PCT_CLEAN', 'FT_PCT_CLEAN', 'EFG_PCT_CLEAN'])
            st.markdown('')
            st.dataframe(team_games, use_container_width=True)

    except:
        pass