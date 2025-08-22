
# Description: config.py contains configuration settings for the BitHorn community bot.
# Author: Rocco Sicilia, u/Sheli4k on Reddit -- https://roccosicilia.com
# Contributors: u/Sheli4k

import telebot
import requests
from config import *
from datetime import datetime, timezone, timedelta

# base config
BOT = telebot.TeleBot(TELEGRAM_API_TOKEN)
SUBREDDIT = SUBREDDIT_NAME
CHAT_ID = TELEGRAM_CHAT_ID
CLIENT_ID = REDDIT_CLIENT_ID
CLIENT_SECRET = REDDIT_CLIENT_SECRET

def get_reddit_token():
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {
        'grant_type': 'client_credentials'
    }
    headers = {'User-Agent': 'BitHornBot/0.2'}
    response = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Error Reddit OAuth: {response.status_code}")
        print(response.text)
        return None

# read today's topics from subreddit
def today_topics(subreddit):
    token = get_reddit_token()
    if not token:
        return "Error Reddit auth.", 0
    url = f"https://oauth.reddit.com/r/{subreddit}/new?limit=50"
    headers = {
        "Authorization": f"bearer {token}",
        "User-Agent": "BitHornBot/0.2"
    }
    response = requests.get(url, headers=headers)
    result = ""
    post_count = 0
    if response.status_code == 200:
        cet = timezone(timedelta(hours=1))
        today = datetime.now(cet).date()
        result += f"Post del {today} su r/{subreddit}:\n\n"
        # indentify posts from today
        for post in response.json()["data"]["children"]:
            created_utc = datetime.fromtimestamp(post["data"]["created_utc"], tz=timezone.utc)
            created_cet = created_utc.astimezone(cet)
            post_date = created_cet.date()
            title = post["data"]["title"]
            link = "https://reddit.com" + post["data"]["permalink"]
            selftext = post["data"].get("selftext", "")
            preview = " ".join(selftext.split()[:10])
            if post_date == today:
                result += f"### {title}\n{preview}...\n{link}\n\n"
                post_count += 1
    else:
        print(f"Error, response status: {response.status_code}")
        print(response.text)
    return result, post_count

result, post_count = today_topics(SUBREDDIT)
if post_count != 0:
    message = result
    BOT.send_message(CHAT_ID, message, disable_web_page_preview=True)
