import requests
import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
from nba_api.stats.static import players, teams
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
import time
import re

st.set_page_config(page_title="Standings",
                   layout="wide")

response = requests.get('https://bleacherreport.com/articles/10101992-does-stephen-curry-have-a-real-goat-argument')
soup = BeautifulSoup(response.text, 'html.parser')

meta_tag = soup.find('meta', {'name': 'pubdate'})
date_string = meta_tag.get('content')
date_time_obj = parser.isoparse(date_string).strftime('%Y-%m-%d %H:%M:%S')
date_time_obj = datetime.strptime(date_time_obj,'%Y-%m-%d %H:%M:%S')
img_tag = soup.find('div', class_='imgWrapper').find('img')
image_src = img_tag['src']
match = re.search(r'/w_(\d+),h_(\d+)', image_src)
old_width = int(match.group(1))
old_height = int(match.group(2))
new_width = old_width * 20
new_height = old_height * 20
image_url = re.sub(r'/w_\d+,h_\d+', f'/w_{new_width},h_{new_height}/', image_src)


