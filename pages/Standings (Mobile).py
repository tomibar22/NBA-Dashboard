import pandas as pd
from datetime import datetime, timedelta
from nba_api.stats.endpoints.leaguestandings import LeagueStandings
import streamlit as st
import plotly.express as px


df = LeagueStandings().get_data_frames()[0]
dff = df.sort_values('TeamCity')

dff = dff.drop(columns=['LeagueID', 'SeasonID', 'TeamID', 'ConferenceRecord', 'DivisionRecord', 'DivisionRank', 'LeagueRank', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
dff['Team'] = dff['TeamCity'] + ' ' + dff['TeamName']

east = dff[dff['Conference']=='East'].sort_values(['WinPCT','Team'], ascending=[False, False])
east = east.reset_index(drop=True)
east.index = east.index + 1

west = dff[dff['Conference']=='West'].sort_values(['WinPCT','Team'], ascending=[False, False])
west = west.reset_index(drop=True)
west.index = west.index + 1

east = east[['Team', 'Record', 'WinPCT', 'strCurrentStreak', 'L10', 'PointsPG', 'OppPointsPG', 'DiffPointsPG']]
east['Status'] = east.index.to_series().apply(lambda x: 'Playoff Qualifiers' if x < 7 else ('Play-In Tournament' if x < 11 else 'Non-Playoff'))
east['WinPCT_str'] = east['WinPCT'].map('{:.1%}'.format)
east['Position'] = range(1, len(east) + 1)

west = west[['Team', 'Record', 'WinPCT', 'strCurrentStreak', 'L10', 'PointsPG', 'OppPointsPG', 'DiffPointsPG']]
west['Status'] = west.index.to_series().apply(lambda x: 'Playoff Qualifiers' if x < 7 else ('Play-In Tournament' if x < 11 else 'Non-Playoff'))
west['WinPCT_str'] = west['WinPCT'].map('{:.1%}'.format)
west['Position'] = range(1, len(east) + 1)

st.header('East')
st.write(east)
st.header('West')
st.write(west)