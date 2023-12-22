import pandas as pd
from nba_api.stats.endpoints import leaguedashteamstats, leaguedashplayerstats
import streamlit as st
import plotly.express as px
from datetime import date
from data_processing import sorted_df, get_current_nba_season, get_team_stats_per_game
st.set_page_config(layout="wide")

stat_options = ['W_PCT', 'PTS', 'EFG_PCT', 'AST', 'REB', 'OREB', 'DREB', 
                'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 
                'BLK', 'STL', 'TOV', 'PF', 'PLUS_MINUS', 
                'FT_PCT', 'FTM', 'FTA']



with st.container(border=True):
    st.markdown("<h2 style='text-align: center; letter-spacing: 4px; word-spacing: 20px; font-size: 50px;'>Teams</h2>", unsafe_allow_html=True)

    cl1, cl2, cl3, cl4, cl5 = st.columns([2,4,2,2,2])
    with cl2:
        stat = st.selectbox('Stat',stat_options, label_visibility='hidden')

    with cl3:
        current_season = get_current_nba_season()
        nba_seasons = [f"{year}-{(year + 1) % 100:02d}" for year in range(1960, int(current_season.split('-')[0]) + 1)]
        season = st.selectbox('Season', nba_seasons[::-1], index=0, label_visibility='hidden')
    with cl4:
        season_type = st.selectbox('Season Type', ['Regular Season', 'Playoffs'], label_visibility='hidden')  


    teams_df = get_team_stats_per_game(season, season_type)  



    def team_stats_leaders(stat):
        percentage_columns = ['FG_PCT', 'FG3_PCT', 'FT_PCT', 'EFG_PCT']
        teams_df[percentage_columns] = (teams_df[percentage_columns] * 100).round(2).astype(int).astype(str) + '%'
        pct_col_dict = {
            'FG_PCT': [stat, 'FGM', 'FGA'],
            'FG3_PCT': [stat, 'FG3M', 'FG3A'],
            'FT_PCT': [stat, 'FTM', 'FTA'],
            'EFG_PCT': [stat, 'FGM', 'FGA']
        }
        if stat in pct_col_dict:
            team_stats_leaders = teams_df.dropna() \
                                            .sort_values(stat, ascending=False) \
                                            .reset_index(drop=True)
        else:
            team_stats_leaders = teams_df.dropna() \
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
        
        team_stats_leaders.index = team_stats_leaders.index +1


        return team_stats_leaders
    
    teams_df = team_stats_leaders(stat)

    cl1, cl2, cl3 = st.columns([1,5,1])
    with cl2:
        pct =  {
        'FG_PCT': [stat, 'FGM', 'FGA'],
        'FG3_PCT': [stat, 'FG3M', 'FG3A'],
        'FT_PCT': [stat, 'FTM', 'FTA'],
        'EFG_PCT': [stat, 'FGM', 'FGA'],
        'W_PCT': [stat, 'W', 'L']
        }
        if 'PCT' in stat:
            if stat == 'W_PCT':
                pass
            else:
                teams_df[stat] = teams_df[stat].str.rstrip('%').astype(float) / 100.0
                # teams_df[stat] = teams_df[stat].map("{:.2%}".format)
            
        fig = px.bar(teams_df.head(10), x='TEAM', y=stat,
                    text=stat,
                    hover_data= pct[stat] if 'PCT' in stat else None,
                    color=stat,
                    color_continuous_midpoint=teams_df[stat].mean(),
                    color_continuous_scale='Greens',
                    # facet_col=stat if stat2 else None
                    )
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


        st.dataframe(teams_df)

