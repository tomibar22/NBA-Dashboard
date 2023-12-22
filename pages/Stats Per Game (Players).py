import pandas as pd
from nba_api.stats.endpoints import leaguedashteamstats, leaguedashplayerstats
import streamlit as st
import plotly.express as px
from datetime import date
from data_processing import sorted_df, get_current_nba_season, get_player_stats_per_game, get_rookie_stats_per_game
st.set_page_config(layout="wide")


teams_df = leaguedashteamstats.LeagueDashTeamStats(per_mode_detailed='PerGame').get_data_frames()[0]
rookie_df = leaguedashplayerstats.LeagueDashPlayerStats(per_mode_detailed='PerGame', player_experience_nullable='Rookie').get_data_frames()[0]


with st.container(border=True):
    st.markdown("<h2 style='text-align: center; letter-spacing: 4px; word-spacing: 20px; font-size: 50px;'>All Players</h2>", unsafe_allow_html=True)

    cl1, cl2, cl3, cl4, cl5 = st.columns([2,4,2,2,2])
    with cl2:
        stat = st.selectbox('Stat',['PTS', 'EFG_PCT', 'AST', 'REB', 'OREB', 'DREB',
                                    'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 
                                    'BLK', 'STL', 'TOV', 'PF', 'PLUS_MINUS', 
                                    'FT_PCT', 'FTM', 'FTA', 'MIN',  'AGE'], label_visibility='hidden')
        pct =  {
                'FG_PCT': [stat, 'FGM', 'FGA'],
                'FG3_PCT': [stat, 'FG3M', 'FG3A'],
                'FT_PCT': [stat, 'FTM', 'FTA'],
                'EFG_PCT': [stat, 'FGM', 'FGA']
                }
        
    with cl3:
        current_season = get_current_nba_season()
        nba_seasons = [f"{year}-{(year + 1) % 100:02d}" for year in range(1960, int(current_season.split('-')[0]) + 1)]
        season = st.selectbox('Season', nba_seasons[::-1], index=0, label_visibility='hidden')
    with cl4:
        season_type = st.selectbox('Season Type', ['Regular Season', 'Playoffs'], label_visibility='hidden')  

    players_df = get_player_stats_per_game(season, season_type) 
    if 'PCT' in stat:
        c1,c2,c3 = st.columns([2,8,2])
        min_value = players_df[players_df[pct[stat][2]] > 0][pct[stat][2]].min()
        max_value = players_df[pct[stat][2]].max()
        slider = c2.slider('Minimum Attempts', min_value, max_value, value=round(max_value / 2, 0), step=1.0, format='%d')
    else:
        slider = None   
    players_df = sorted_df(players_df,stat, slider).head(50)

    cl1, cl2, cl3 = st.columns([1,5,1])
    with cl2:
        if 'PCT' in stat:
            players_df[stat] = players_df[stat].str.rstrip('%').astype('float') / 100.0

        fig = px.bar(players_df.head(10), x='PLAYER', y=stat,
                    text=stat,
                    hover_data= pct[stat] if 'PCT' in stat else None,
                    color=stat,
                    color_continuous_midpoint=players_df[stat].mean(),
                    color_continuous_scale='Blues')
        # fig.update_traces(orientation='h')
        if 'PCT' in stat:
            fig.update_traces(texttemplate='%{text:.0%}'+'<br>%{customdata[0]}/%{customdata[1]}', textposition='inside',
                                hovertemplate='%{x}'+'<br>%{text:.0%}'+'<br>%{customdata[0]} / %{customdata[1]}')
        else:
            fig.update_traces(texttemplate='%{text}', textposition='inside',
                                hovertemplate='%{x}'+'<br>%{text}'+f' {stat}')
        fig.update_layout(coloraxis_showscale=False,
                        xaxis=dict(title_text='', tickfont=dict(size=17)),
                        yaxis=dict(title_text='', tickfont=dict(size=17)),
                        font=dict(size=17),
                        hoverlabel=dict(font_size=17),
                        height=600)
        st.plotly_chart(fig, use_container_width=True)


        st.dataframe(players_df)






with st.container(border=True):
    st.markdown("<h2 style='text-align: center; letter-spacing: 4px; word-spacing: 20px; font-size: 50px;'>Rookies</h2>", unsafe_allow_html=True)

    cl1, cl2, cl3, cl4 = st.columns([2,6,2,2])
    with cl2:
        stat = st.selectbox('Stat',['PTS', 'EFG_PCT',  'AST', 'REB', 'OREB', 'DREB', 
                                    'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 
                                    'BLK', 'STL', 'TOV', 'PF', 'PLUS_MINUS', 
                                    'FT_PCT', 'FTM', 'FTA', 'MIN',  'AGE'], label_visibility='hidden', key='rookie-stats')
        
    with cl3:
        season_type = st.selectbox('Season Type', ['Regular Season', 'Playoffs'], label_visibility='hidden', key='rookie-season-type')   

    rookie_df = get_rookie_stats_per_game(season_type)   
    if 'PCT' in stat:
        c1,c2,c3 = st.columns([2,8,2])
        min_value = rookie_df[rookie_df[pct[stat][2]] > 0][pct[stat][2]].min()
        max_value = rookie_df[pct[stat][2]].max()
        slider = c2.slider('Minimum Attempts', min_value, max_value, value=max_value / 2, step=1.0, format='%d')
    else:
        slider = None    
    rookie_df = sorted_df(rookie_df,stat,slider).head(50)

    cl1, cl2, cl3 = st.columns([1,5,1])
    with cl2:
        if 'PCT' in stat:
            rookie_df[stat] = rookie_df[stat].str.rstrip('%').astype('float') / 100.0
            pct =  {
                    'FG_PCT': [stat, 'FGM', 'FGA'],
                    'FG3_PCT': [stat, 'FG3M', 'FG3A'],
                    'FT_PCT': [stat, 'FTM', 'FTA'],
                    'EFG_PCT': [stat, 'FGM', 'FGA']
                    }
        fig = px.bar(rookie_df.head(10), x='PLAYER', y=stat,
                    text=stat,
                    hover_data= pct[stat] if 'PCT' in stat else None,
                    color=stat,
                    color_continuous_midpoint=rookie_df[stat].mean(),
                    color_continuous_scale='Purples')
        # fig.update_traces(orientation='h')
        if 'PCT' in stat:
            fig.update_traces(texttemplate='%{text:.0%}'+'<br>%{customdata[0]}/%{customdata[1]}', textposition='inside',
                                hovertemplate='%{x}'+'<br>%{text:.0%}'+'<br>%{customdata[0]} / %{customdata[1]}')
        else:
            fig.update_traces(texttemplate='%{text}', textposition='inside',
                                hovertemplate='%{x}'+'<br>%{text}'+f' {stat}')
        fig.update_layout(coloraxis_showscale=False,
                        xaxis=dict(title_text='', tickfont=dict(size=17)),
                        yaxis=dict(title_text='', tickfont=dict(size=17)),
                        font=dict(size=17),
                        hoverlabel=dict(font_size=17),
                        height=600)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(rookie_df)