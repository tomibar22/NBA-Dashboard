import pandas as pd
from datetime import datetime, timedelta
from nba_api.stats.endpoints.leaguestandings import LeagueStandings
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Standings",
                   layout="wide")

logos = ['https://content.sportslogos.net/logos/6/220/thumbs/22081902021.gif', 'https://content.sportslogos.net/logos/6/213/thumbs/slhg02hbef3j1ov4lsnwyol5o.gif', 'https://content.sportslogos.net/logos/6/3786/thumbs/hsuff5m3dgiv20kovde422r1f.gif', 'https://content.sportslogos.net/logos/6/5120/thumbs/512019262015.gif', 'https://content.sportslogos.net/logos/6/221/thumbs/hj3gmh82w9hffmeh3fjm5h874.gif', 'https://content.sportslogos.net/logos/6/222/thumbs/22253692023.gif',
         'https://content.sportslogos.net/logos/6/228/thumbs/22834632018.gif', 'https://content.sportslogos.net/logos/6/229/thumbs/22989262019.gif', 'https://content.sportslogos.net/logos/6/223/thumbs/22321642018.gif', 'https://content.sportslogos.net/logos/6/235/thumbs/23531522020.gif', 'https://content.sportslogos.net/logos/6/230/thumbs/23068302020.gif', 'https://content.sportslogos.net/logos/6/224/thumbs/22448122018.gif',
         'https://content.sportslogos.net/logos/6/236/thumbs/23637762019.gif', 'https://content.sportslogos.net/logos/6/237/thumbs/23773242024.gif', 'https://content.sportslogos.net/logos/6/231/thumbs/23143732019.gif', 'https://content.sportslogos.net/logos/6/214/thumbs/burm5gh2wvjti3xhei5h16k8e.gif', 'https://content.sportslogos.net/logos/6/225/thumbs/22582752016.gif', 'https://content.sportslogos.net/logos/6/232/thumbs/23296692018.gif', 
         'https://content.sportslogos.net/logos/6/4962/thumbs/496292922024.gif', 'https://content.sportslogos.net/logos/6/216/thumbs/21671702024.gif', 'https://content.sportslogos.net/logos/6/2687/thumbs/khmovcnezy06c3nm05ccn0oj2.gif', 'https://content.sportslogos.net/logos/6/217/thumbs/wd9ic7qafgfb0yxs7tem7n5g4.gif', 'https://content.sportslogos.net/logos/6/218/thumbs/21870342016.gif', 'https://content.sportslogos.net/logos/6/238/thumbs/23843702014.gif',
         'https://content.sportslogos.net/logos/6/239/thumbs/23997252018.gif', 'https://content.sportslogos.net/logos/6/240/thumbs/24040432017.gif', 'https://content.sportslogos.net/logos/6/233/thumbs/23325472018.gif', 'https://content.sportslogos.net/logos/6/227/thumbs/22770242021.gif', 'https://content.sportslogos.net/logos/6/234/thumbs/23485132023.gif', 'https://content.sportslogos.net/logos/6/219/thumbs/21956712016.gif']


df = LeagueStandings().get_data_frames()[0]
dff = df.sort_values('TeamCity')
dff['logo'] = logos
dff = dff.drop(columns=['LeagueID', 'SeasonID', 'TeamID', 'ConferenceRecord', 'DivisionRecord', 'DivisionRank', 'LeagueRank', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
dff['Team'] = dff['TeamCity'] + ' ' + dff['TeamName']

east = dff[dff['Conference']=='East'].sort_values(['WinPCT','Team'], ascending=[False, False])
east = east.reset_index(drop=True)
east.index = east.index + 1

west = dff[dff['Conference']=='West'].sort_values(['WinPCT','Team'], ascending=[False, False])
west = west.reset_index(drop=True)
west.index = west.index + 1

east = east[['Team', 'Record', 'WinPCT', 'strCurrentStreak', 'L10', 'PointsPG', 'OppPointsPG', 'DiffPointsPG', 'logo']]
east['Status'] = east.index.to_series().apply(lambda x: 'Playoff Qualifiers' if x < 7 else ('Play-In Tournament' if x < 11 else 'Non-Playoff'))
east['WinPCT_str'] = east['WinPCT'].map('{:.1%}'.format)
east['Position'] = range(1, len(east) + 1)

west = west[['Team', 'Record', 'WinPCT', 'strCurrentStreak', 'L10', 'PointsPG', 'OppPointsPG', 'DiffPointsPG', 'logo']]
west['Status'] = west.index.to_series().apply(lambda x: 'Playoff Qualifiers' if x < 7 else ('Play-In Tournament' if x < 11 else 'Non-Playoff'))
west['WinPCT_str'] = west['WinPCT'].map('{:.1%}'.format)
west['Position'] = range(1, len(east) + 1)


with st.container(border=True):
    c1, c2, c3, c4, c5 = st.columns([0.7,12,1,12,0.7])
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