import requests
import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
from nba_api.stats.static import players, teams
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser
import time
import re
from data_processing import get_tweets

st.set_page_config(page_title="Player Stats Browser",
                   layout="wide")



def retry(func, retries=3):
    def retry_wrapper(*args, **kwargs):
        attempts = 0
        while attempts < retries:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                print(e)
                time.sleep(5)
                attempts += 1

    return retry_wrapper


if "player" not in st.session_state:
    st.session_state.player = None

if "team" not in st.session_state:
    st.session_state.team = None


def clear_box():
    if st.session_state.player:
        st.session_state.team = None

    if st.session_state.team:
        st.session_state.player = None



players_df = pd.DataFrame(players.get_active_players())
player_names = list(players_df['full_name'])
teams_df = pd.DataFrame(teams.get_teams())
team_nicknames = list(teams_df['nickname'])

c1,c2,c3,c4,c5=st.columns([3,2,0.1,2,3])
player = c2.selectbox('player search' ,player_names, placeholder='Search by player...', index=None, label_visibility='hidden', key="player", on_change=clear_box)
c3.markdown('<h3 style="padding-top: 27px; text-align: center">/</h3>', unsafe_allow_html=True)
team = c4.selectbox('team search' ,team_nicknames, placeholder='Search by team...', index=None, label_visibility='hidden', key="team", on_change=clear_box)

if team:
    team = team.lower().replace(' ', '-')

if player:
    player = player.split(' ')[1]


@st.cache_data(ttl=timedelta(hours=1))
def get_news(source):

    url = "https://nba-latest-news.p.rapidapi.com/articles"

    querystring = {"player":player,
                   "team": team,
                   "source": source,
                   "limit": "10"}

    headers = {
        "X-RapidAPI-Key": "33dd98ace4msh868aeb43c6ceb9fp1ba196jsnf68435311c26",
        "X-RapidAPI-Host": "nba-latest-news.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()

nba_news = get_news("nba")
nba_canada_news = get_news("nba-canada")
slam_news = get_news("slam")
bleacher_news = get_news("bleacher-report")
news = nba_news + nba_canada_news + slam_news + bleacher_news


@retry
@st.cache_data
def get_article_date(url, source):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        if source == 'nba':
            date_string = soup.find('time', class_='ArticleHeader_ahDate__J3fwr')
            date_string = date_string.get_text(strip=True)
            date_string = date_string.replace('Updated on ', '')
            date_time_obj = datetime.strptime(date_string, '%B %d, %Y %I:%M %p')
            img_tag = soup.find('div', class_='ArticleContent_article__NBhQ8').find('img')
            image_url = img_tag['src']
            return date_time_obj, image_url if img_tag else date_time_obj
        
        if source == "nba_canada":
            date_string = soup.find('time', class_='published-datetime')
            date_string = date_string.get('datetime', '')
            date_time_obj = parser.isoparse(date_string).strftime('%Y-%m-%d %H:%M:%S')
            date_time_obj = datetime.strptime(date_time_obj, '%Y-%m-%d %H:%M:%S')
            img_tag = soup.find('picture').find('img')
            image_url = img_tag['src']
            return date_time_obj, image_url if img_tag else date_time_obj
        
        if source == 'slam':
            meta_tag = soup.find('meta', {'property': 'article:published_time'})
            date_string = meta_tag.get('content')
            date_time_obj = parser.isoparse(date_string).strftime('%Y-%m-%d %H:%M:%S')
            date_time_obj = datetime.strptime(date_time_obj,'%Y-%m-%d %H:%M:%S')
            div_tag = soup.find('div', class_='blog-post-header-img')
            div_tag = soup.find('div', class_='blog-post-header-img')
            data_bg_attribute = div_tag['data-bg']
            start_index = data_bg_attribute.find('url("') + len('url("')
            end_index = data_bg_attribute.find('")', start_index)
            image_url = data_bg_attribute[start_index:end_index]
            return date_time_obj, image_url if div_tag else date_time_obj
        
        if source == 'bleacher_report':
            meta_tag = soup.find('meta', {'name': 'pubdate'})
            date_string = meta_tag.get('content')
            date_time_obj = parser.isoparse(date_string).strftime('%Y-%m-%d %H:%M:%S')
            date_time_obj = datetime.strptime(date_time_obj,'%Y-%m-%d %H:%M:%S')
            img_tag = soup.find('div', class_='imgWrapper').find('img')
            image_src = img_tag['src']
            match = re.search(r'/w_(\d+),h_(\d+)', image_src)
            old_width = int(match.group(1))
            old_height = int(match.group(2))
            new_width = old_width * 30
            new_height = old_height * 30
            image_url = re.sub(r'/w_\d+,h_\d+', f'/w_{new_width},h_{new_height}/', image_src)
            return date_time_obj, image_url if img_tag else date_time_obj

    except Exception as e:
        print(f"Error fetching date for {url}: {e}")
        return None


progress_text = "Operation in progress. Please wait."
my_bar = st.progress(0, text=progress_text)



# Fetch date and image for each article
for idx, article in enumerate(news):
    article_url = article['url']
    article_source = article['source']
    result = get_article_date(article_url, article_source)
    
    if result:
        article_date, article_image = result
        article['date'] = article_date
        article['image'] = article_image
    else:
        # Handle the case where get_article_date returns None
        article['date'] = article_date
        article['image'] = ""

news = sorted(news, key=lambda x: x['date'], reverse=True)

for percent_complete in range(100):
    time.sleep(0.01)
    my_bar.progress(percent_complete + 1, text=progress_text)
time.sleep(1)
my_bar.empty()






c1,c2,c3,c4,c5 = st.columns([1,2.5,0.3,2,1])
with c2:
    st.markdown('<h2 style="text-align: center;">Articles</h2>', unsafe_allow_html=True)
    for article in news:
        st.markdown('##')
        with st.container(border=True):
            st.markdown(f'<h2 style="text-align: center; padding-bottom: 37px"><a href={article["url"]} style="text-decoration: none; color: #5DADE2;">{article["title"]}</a></h2>',
                            unsafe_allow_html=True)
            try:
                st.image(article["image"], use_column_width=True)
            except:
                pass
            st.markdown(f'<p style="text-align: center;">{article["date"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="text-align: center;">{article["source"]}</p>', unsafe_allow_html=True)



            
with c4:  
    tweets_df = get_tweets()

    st.markdown('<h2 style="text-align: center;">Tweets</h2>', unsafe_allow_html=True)
    st.markdown('##')

    for index, row in tweets_df.iterrows():
        with st.container(border=True):
            st.markdown(row['User Name'], unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 22px;'>{row['Text']}</p", unsafe_allow_html=True)
            st.markdown(f"{row['Likes']} Likes", unsafe_allow_html=True)
            if row['Pictures']:
                st.image(row['Pictures'], unsafe_allow_html=True)
            st.markdown(row['Date'], unsafe_allow_html=True)
            st.markdown(row['Link'], unsafe_allow_html=True)
        st.markdown('')
