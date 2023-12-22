import pandas as pd
from datetime import datetime, timedelta
from nba_api.stats.endpoints.leaguestandings import LeagueStandings
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Standings",
                   layout="wide")

colors = ['#E03A3E', '#007A33', '#FFFFFF', '#1D1160', '#CE1141', '#860038',
         '#00538C', '#0E2240', '#C8102E', '#1D428A', '#CE1141', '#002D62',
         '#C8102E', '#552583', '#5D76A9', '#98002E', '#00471B', '#0C2340', 
         '#0C2340', '#006BB6', '#007AC1', '#0077C0', '#006BB6', '#1D1160',
         '#E03A3E', '#5A2D81', '#C4CED4', '#CE1141', '#002B5C', '#002B5C']


df = LeagueStandings().get_data_frames()[0]
dff = df.sort_values('TeamCity')
dff['color'] = colors
dff = dff.drop(columns=['LeagueID', 'SeasonID', 'TeamID', 'ConferenceRecord', 'DivisionRecord', 'DivisionRank', 'LeagueRank', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
dff['Team'] = dff['TeamCity'] + ' ' + dff['TeamName']

east = dff[dff['Conference']=='East'].sort_values(['WinPCT','Team'], ascending=[False, False])
east = east.reset_index(drop=True)
east.index = east.index + 1

west = dff[dff['Conference']=='West'].sort_values(['WinPCT','Team'], ascending=[False, False])
west = west.reset_index(drop=True)
west.index = west.index + 1

east = east[['Team', 'Record', 'WinPCT', 'strCurrentStreak', 'L10', 'PointsPG', 'OppPointsPG', 'DiffPointsPG', 'color']]
east['Status'] = east.index.to_series().apply(lambda x: 'Playoff Qualifiers' if x < 7 else ('Play-In Tournament' if x < 11 else 'Non-Playoff'))
east['WinPCT_str'] = east['WinPCT'].map('{:.1%}'.format)
east['Position'] = range(1, len(east) + 1)

west = west[['Team', 'Record', 'WinPCT', 'strCurrentStreak', 'L10', 'PointsPG', 'OppPointsPG', 'DiffPointsPG', 'color']]
west['Status'] = west.index.to_series().apply(lambda x: 'Playoff Qualifiers' if x < 7 else ('Play-In Tournament' if x < 11 else 'Non-Playoff'))
west['WinPCT_str'] = west['WinPCT'].map('{:.1%}'.format)
west['Position'] = range(1, len(east) + 1)


with st.container(border=True):
    c1, c2, c3, c4, c5 = st.columns([0.7,13,1,13,0.7])
    with c4:
        st.markdown(f"<h2 style='text-align: center; letter-spacing: 4px; word-spacing: 20px; font-size: 40px;'>EAST</h2>", unsafe_allow_html=True)
        fig = px.bar(east, x='WinPCT', y='Team',
                    orientation='h', 
                    text=east.apply(lambda row: f"  {row['Record']}   <b>|</b>   {row['WinPCT_str']}   <b>|</b>   {row['strCurrentStreak']}   ", axis=1),
                    hover_data=['L10', 'DiffPointsPG'],
                    color='Status',
                    color_discrete_sequence=['#145A32', '#154360', '#4D5656'],
                    height=1050)
        
        fig.update_yaxes(categoryorder='array', categoryarray=east['Team'][::-1])
        fig.update_xaxes(range=[0, east['WinPCT'].max()])
        fig.update_traces(hovertemplate='L10: %{customdata[0]}   DPPG: %{customdata[1]}',
                        insidetextfont=dict(size=20),
                        outsidetextfont=dict(size=20))
        fig.update_layout(font=dict(size=18),
                        xaxis=dict(title_text='', showticklabels=False),
                        yaxis=dict(title_text='', tickmode='array', tickvals=east['Team'], ticktext=east.apply(lambda row: f"<b><span style='font-size: 30px;'>{row['Team']}</span></b> <span style='font-size: 16px;'>#{row['Position']}</span>", axis=1), tickfont=dict(size=22)),
                        hoverlabel=dict(font_size=20),
                        showlegend=False,
                        hoverlabel_align = 'left')
        
        line_positions = [4.5, 8.5]
        shapes = [
            dict(
                type='line',
                x0=0,
                x1=1,
                y0=position,
                y1=position,
                line=dict(color='#CACFD2', width=2, dash='dash')
            )
            for position in line_positions
        ]

        fig.update_layout(shapes=shapes)


        st.plotly_chart(fig, use_container_width=True)


    with c2:
            st.markdown(f"<h2 style='text-align: center; letter-spacing: 4px; word-spacing: 20px; font-size: 40px;'>WEST</h2>", unsafe_allow_html=True)
            fig = px.bar(west, x='WinPCT', y='Team',
                    orientation='h', 
                    text=west.apply(lambda row: f"  {row['Record']}   <b>|</b>   {row['WinPCT_str']}   <b>|</b>   {row['strCurrentStreak']}   ", axis=1),
                    hover_data=['L10', 'DiffPointsPG'],
                    color='Status',
                    color_discrete_sequence=['#145A32', '#154360', '#4D5656'],
                    height=1050)
        
            fig.update_yaxes(categoryorder='total ascending')
            fig.update_xaxes(range=[0, west['WinPCT'].max()])
            fig.update_traces(hovertemplate='L10: %{customdata[0]}   DPPG: %{customdata[1]}',
                            insidetextfont=dict(size=20),
                            outsidetextfont=dict(size=20))
            fig.update_layout(font=dict(size=18),
                            xaxis=dict(title_text='', showticklabels=False),
                            yaxis=dict(title_text='', tickmode='array', tickvals=west['Team'], ticktext=west.apply(lambda row: f"<b><span style='font-size: 30px;'>{row['Team']}</span></b> <span style='font-size: 16px;'>#{row['Position']}</span>", axis=1), tickfont=dict(size=22)),
                            hoverlabel=dict(font_size=20),
                            showlegend=False)
            line_positions = [4.5, 8.5]
            shapes = [
                dict(
                    type='line',
                    x0=0,
                    x1=1,
                    y0=position,
                    y1=position,
                    line=dict(color='#CACFD2', width=2, dash='dash')
                )
                for position in line_positions
            ]
            fig.update_layout(shapes=shapes)
            
            st.plotly_chart(fig, use_container_width=True)