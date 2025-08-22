
# Description: config.py contains configuration settings for the BitHorn community bot.
# Author: Rocco Sicilia, u/Sheli4k on Reddit -- https://roccosicilia.com
# Contributors: u/Sheli4k

import telebot
import requests
from config import *
from datetime import datetime, timezone, timedelta

BOT = telebot.TeleBot(TELEGRAM_API_TOKEN)
SUBREDDIT = SUBREDDIT_NAME
CHAT_ID = TELEGRAM_CHAT_ID

def today_topics(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=50"
    headers = {"User-Agent": "BitHornBot/0.1"}
    response = requests.get(url, headers=headers)
    result = ""
    post_count = 0
    if response.status_code == 200:
        cet = timezone(timedelta(hours=1))  # Central European Time (GMT+1)
        today = datetime.now(cet).date()
        result += f"Post del {today} su r/{subreddit}:\n\n"
        for post in response.json()["data"]["children"]:
            created_utc = datetime.fromtimestamp(post["data"]["created_utc"], tz=timezone.utc)
            created_cet = created_utc.astimezone(cet)
            post_date = created_cet.date()
            title = post["data"]["title"]
            link = "https://reddit.com" + post["data"]["permalink"]
            selftext = post["data"].get("selftext", "")
            preview = " ".join(selftext.split()[:10])
            if post_date == today:
                result += f"### {title}\n {preview}...\n {link}\n\n"
                post_count += 1
    return result, post_count

result, post_count = today_topics(SUBREDDIT)
if post_count != 0:
    message = result
    BOT.send_message(CHAT_ID, message, disable_web_page_preview=True)