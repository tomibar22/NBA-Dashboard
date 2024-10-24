import pandas as pd
from datetime import date, timedelta
from nba_api.stats.endpoints import leaguegamelog, boxscoretraditionalv2, playbyplayv2, teamgamelog, leaguedashplayerstats, playergamelog, leaguedashteamstats
import streamlit as st
from ntscraper import Nitter

def sorted_df(df, stat, slider):
    current_columns = df.columns.tolist()
    percentage_columns = ['FG_PCT', 'FG3_PCT', 'FT_PCT', 'TS_PCT']
    df[percentage_columns] = (df[percentage_columns] * 100).round(0).astype(int).astype(str) + '%'

    pct_col_dict = {
        'FG_PCT': [stat, 'FGM', 'FGA'],
        'FG3_PCT': [stat, 'FG3M', 'FG3A'],
        'FT_PCT': [stat, 'FTM', 'FTA'],
        'TS_PCT': [stat, 'FGM', 'FGA']
    }

    if stat in pct_col_dict:
        df = df[df[pct_col_dict[stat][2]] >= slider].dropna() \
                                            .drop_duplicates() \
                                            .reset_index(drop=True)
        df = df.sort_values(stat, ascending=False)
 

        columns_to_move = pct_col_dict[stat]
        
        for col in columns_to_move:
            current_columns.remove(col)

        for col in reversed(columns_to_move):
            current_columns.insert(2, col)

        df = df[current_columns]

    else:
        df = df.dropna() \
                                    .drop_duplicates() \
                                    .sort_values(stat, ascending=False) \
                                    .reset_index(drop=True)
        current_columns.remove(stat)
        current_columns.insert(2, stat)
        df = df[current_columns]

    df = df.reset_index(drop=True)
    df.index = df.index + 1

    return df




def get_current_nba_season():
    today = date.today()
    if today.month >= 10:
        return f"{today.year}-{(today.year + 1) % 100:02d}"
    else:
        return f"{today.year - 1}-{today.year % 100:02d}"
current_season = get_current_nba_season()






def get_player_stats_per_game(season, season_type):
    players_df = leaguedashplayerstats.LeagueDashPlayerStats(per_mode_detailed='PerGame', season=season, season_type_all_star=season_type).get_data_frames()[0]
    players_df = players_df[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'PTS', 'AST', 'REB', 'OREB', 'DREB', 'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 'BLK', 'STL', 'TOV', 'PF', 'PLUS_MINUS', 'FT_PCT', 'FTM', 'FTA', 'MIN',  'AGE']]
    players_df = players_df.rename(columns={'TEAM_ABBREVIATION': 'TEAM',
                                        'PLAYER_NAME': 'PLAYER'})
    condition = players_df['FGA'] >= 10
    players_df.loc[condition, 'TS_PCT'] = players_df.loc[condition, 'PTS'] / (2 * (players_df.loc[condition, 'FGA'] + 0.44 * players_df.loc[condition, 'FTA']))
    players_df = players_df.dropna(subset='TS_PCT')
    return players_df





def get_rookie_stats_per_game(season_type):
    rookie_df = leaguedashplayerstats.LeagueDashPlayerStats(per_mode_detailed='PerGame', player_experience_nullable='Rookie', season_type_all_star=season_type).get_data_frames()[0]
    rookie_df = rookie_df[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'PTS', 'AST', 'REB', 'OREB', 'DREB', 'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 'BLK', 'STL', 'TOV', 'PF', 'PLUS_MINUS', 'FT_PCT', 'FTM', 'FTA', 'MIN',  'AGE']]
    rookie_df = rookie_df.rename(columns={'TEAM_ABBREVIATION': 'TEAM',
                                        'PLAYER_NAME': 'PLAYER'})
    condition = rookie_df['FGA'] >= 5
    rookie_df.loc[condition, 'TS_PCT'] = rookie_df.loc[condition, 'PTS'] / (2 * (rookie_df.loc[condition, 'FGA'] + 0.44 * rookie_df.loc[condition, 'FTA']))
    rookie_df = rookie_df.dropna(subset='TS_PCT')
    return rookie_df


def get_team_stats_per_game(season, season_type):
    teams_df = leaguedashteamstats.LeagueDashTeamStats(per_mode_detailed='PerGame', season=season, season_type_all_star=season_type).get_data_frames()[0]
    teams_df['WL'] = teams_df['W'].astype(str) + '-' + teams_df['L'].astype(str)
    teams_df = teams_df.drop(columns=['W', 'L'])
    teams_df = teams_df[['TEAM_NAME', 'WL', 'W_PCT', 'PTS', 'AST', 'REB', 'OREB', 'DREB', 'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 'BLK', 'STL', 'TOV', 'PF', 'PLUS_MINUS', 'FT_PCT', 'FTM', 'FTA']]
    teams_df = teams_df.rename(columns={'TEAM_NAME': 'TEAM'})
    condition = teams_df['FGA'] >= 10
    teams_df.loc[condition, 'TS_PCT'] = teams_df.loc[condition, 'PTS'] / (2 * (teams_df.loc[condition, 'FGA'] + 0.44 * teams_df.loc[condition, 'FTA']))
    return teams_df



def get_player_games(player_id, season, season_type, stat):
    player_games = playergamelog.PlayerGameLog(player_id=player_id, season=season, season_type_all_star=season_type).get_data_frames()[0]
    player_games = player_games.drop(columns=['SEASON_ID', 'Player_ID', 'Game_ID', 'VIDEO_AVAILABLE'])
    player_games = player_games[['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'AST', 'FG_PCT', 'FGM', 'FGA', 'FG3_PCT', 'FG3M', 'FG3A', 
                                'REB', 'OREB', 'DREB', 'BLK', 'STL', 'TOV', 'PF', 'PLUS_MINUS', 'FT_PCT', 'FTM', 'FTA', 'MIN']]
    columns_to_convert = ['PTS', 'AST', 'REB', 'FGM', 'FGA', 'FG3M', 'FG3A', 'BLK', 'STL', 'PLUS_MINUS', 'FTM', 'FTA', 'PF', 'MIN']
    player_games[columns_to_convert] = player_games[columns_to_convert].astype(int)
    condition = player_games['FGA'] >= 10
    player_games.loc[condition, 'TS_PCT'] = player_games.loc[condition, 'PTS'] / (2 * (player_games.loc[condition, 'FGA'] + 0.44 * player_games.loc[condition, 'FTA']))
    player_games = player_games.dropna(subset='TS_PCT')
    player_games[['FG_PCT_CLEAN', 'FG3_PCT_CLEAN', 'FT_PCT_CLEAN', 'TS_PCT_CLEAN']] = player_games[['FG_PCT', 'FG3_PCT', 'FT_PCT', 'TS_PCT']]
    player_games[['FG_PCT_CLEAN', 'FG3_PCT_CLEAN', 'FT_PCT_CLEAN', 'TS_PCT_CLEAN']] = player_games[['FG_PCT_CLEAN', 'FG3_PCT_CLEAN', 'FT_PCT_CLEAN', 'TS_PCT']].apply(pd.to_numeric, errors='coerce')
    percentage_columns = ['FG_PCT', 'FG3_PCT', 'FT_PCT',  'TS_PCT']
    player_games[percentage_columns] = (player_games[percentage_columns] * 100).round(0).astype(int).astype(str) + '%'

    if stat:
        columns_to_move_mapping = {
        'FG_PCT': [stat, 'FGM', 'FGA'],
        'FG3_PCT': [stat, 'FG3M', 'FG3A'],
        'FT_PCT': [stat, 'FTM', 'FTA']
         }
        current_columns = player_games.columns.tolist()
        new_position = 3
        if stat in columns_to_move_mapping:
            columns_to_move = columns_to_move_mapping[stat]

            for col in columns_to_move:
                current_columns.remove(col)

            for col in reversed(columns_to_move):
                current_columns.insert(new_position, col)

            player_games = player_games[current_columns].set_index(player_games.columns[0])

        else:
            current_columns.remove(stat)
            current_columns.insert(new_position, stat)
            player_games = player_games[current_columns].set_index(player_games.columns[0])
    
    return player_games

@st.cache_data(ttl=timedelta(hours=1))
def get_tweets():
    # Expanded list of Nitter instances
    instances = [
        "https://nitter.net",
        "https://nitter.1d4.us",
        "https://nitter.kavin.rocks",
        "https://nitter.unixfox.eu",
        "https://nitter.401.pw",
        "https://nitter.cz",
        "https://nitter.privacydev.net",
        "https://nitter.projectsegfau.lt",
        "https://twitter.censors.us",
        "https://nitter.soopy.moe",
        "https://nitter.rawbit.ninja",
        "https://nitter.cutelab.space"
    ]
    
    def try_get_tweets(username, scraper, retries=3):
        for attempt in range(retries):
            try:
                time.sleep(1)  # Add delay between requests
                result = scraper.get_tweets(username, mode='user', number=5)
                if result and 'tweets' in result and result['tweets']:
                    return result
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {username}: {e}")
                if attempt == retries - 1:
                    return {'tweets': []}
                time.sleep(2 ** attempt)  # Exponential backoff
        return {'tweets': []}

    # Try different instances until one works
    tweets = []
    for instance in instances:
        try:
            print(f"Trying instance: {instance}")
            scraper = Nitter(
                instance=instance,
                take_first=True,
                skip_instance_check=True  # Skip initial check which often fails
            )
            
            # Get tweets from all users
            users = [
                'wojespn', 'ShamsCharania', 'TheSteinLine', 'WindhorstESPN',
                'ChrisBHaynes', 'Rachel__Nichols', 'stevejones20', 
                'NekiasNBA', 'KevinOConnorNBA', 'ZachLowe_NBA'
            ]
            
            # Try to get at least one successful user's tweets
            success = False
            all_tweets = []
            
            for user in users:
                user_tweets = try_get_tweets(user, scraper)
                if user_tweets and 'tweets' in user_tweets and user_tweets['tweets']:
                    success = True
                    all_tweets.extend(user_tweets['tweets'])
                    print(f"Successfully fetched tweets for {user}")
            
            if success:
                tweets = all_tweets
                print(f"Successfully using instance: {instance}")
                break
            
        except Exception as e:
            print(f"Failed to use instance {instance}: {e}")
            continue
    
    # Process tweets with better error handling
    tweet_data = []
    text_check = set()
    
    for tweet in tweets:
        try:
            # Skip if tweet is not in expected format
            if not isinstance(tweet, (dict, list)):
                continue
                
            # Handle both single tweets and tweet lists
            tweet_dict = tweet[0] if isinstance(tweet, list) else tweet
            
            # Extract text and check for duplicates
            text = tweet_dict.get('text', '').strip()
            if not text or text in text_check:
                continue
            
            # Get user information
            user_info = tweet_dict.get('user', {})
            user_name = user_info.get('name', '')
            if not user_name:
                continue
                
            # Extract tweet information
            tweet_info = {
                'User Name': user_name,
                'Text': text,
                'Date': tweet_dict.get('date', ''),
                'Likes': tweet_dict.get('stats', {}).get('likes', 0),
                'Link': tweet_dict.get('link', ''),
                'Pictures': ', '.join(tweet_dict.get('pictures', [])) if 'pictures' in tweet_dict else ''
            }
            
            # Only add tweets with valid dates
            if tweet_info['Date']:
                tweet_data.append(tweet_info)
                text_check.add(text)
            
        except Exception as e:
            print(f"Error processing tweet: {e}")
            continue
    
    if not tweet_data:
        print("No tweets were successfully fetched")
        return pd.DataFrame(columns=['User Name', 'Text', 'Date', 'Likes', 'Link', 'Pictures'])
    
    df = pd.DataFrame(tweet_data)
    
    # Handle date conversion with multiple formats
    def parse_date(date_str):
        try:
            # Try the standard format first
            return pd.to_datetime(date_str, format="%b %d, %Y · %I:%M %p UTC")
        except:
            try:
                # Try parsing with dateutil as fallback
                return pd.to_datetime(parser.parse(date_str))
            except:
                return pd.to_datetime('now')

    df['Date'] = df['Date'].apply(parse_date)
    
    # Sort and clean up the dataframe
    tweets_df = df.sort_values(by='Date', ascending=False).reset_index(drop=True)
    
    # Add debug information
    print(f"Successfully processed {len(tweets_df)} tweets")
    
    return tweets_df

def display_tweets(tweets_df):
    """Separate function to handle tweet display"""
    if tweets_df.empty:
        st.warning("Unable to fetch tweets at this time. Please try again later.")
        return
        
    st.markdown('<h2 style="text-align: center;">Tweets</h2>', unsafe_allow_html=True)
    st.markdown('##')
    
    for index, row in tweets_df.iterrows():
        with st.container(border=True):
            try:
                st.markdown(f"<b>{row['User Name']}</b> [{row['Date'] - timedelta(hours=5)}]", unsafe_allow_html=True)
                st.markdown(f"<span style='font-size: 22px;'>{row['Text']}</span>", unsafe_allow_html=True)
                st.markdown(f"{row['Likes']} Likes", unsafe_allow_html=True)
                if row['Pictures']:
                    st.image(row['Pictures'].split(', '))
                st.markdown(row['Link'], unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error displaying tweet: {str(e)}")
        st.markdown('')
