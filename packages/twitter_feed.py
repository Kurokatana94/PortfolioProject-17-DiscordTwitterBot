from googletrans import Translator
from dotenv import load_dotenv
import feedparser
import tweepy
import discord
import asyncio
import html
import os
import re

load_dotenv()

TWITTER_BEARER=os.getenv("TWITTER_BEARER")
TWITTER_API_KEY=os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET=os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN=os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

PRICONNE_RSS = os.getenv("PRICONNE_RSS")
UMAMUSUME_RSS = os.getenv("UMAMUSUME_RSS")

DISCORD_PRICONNE_TWITTER_CHANNEL_ID=int(os.getenv("DISCORD_PRICONNE_TWITTER_CHANNEL_ID"))
DISCORD_UMAMUSUME_TWITTER_CHANNEL_ID=int(os.getenv("DISCORD_UMAMUSUME_TWITTER_CHANNEL_ID"))
DISCORD_TEST_CHANNEL_ID=int(os.getenv("DISCORD_TEST_CHANNEL_ID"))

TWITTER_TARGET_USERS_CHANNELS = {
    "priconne_redive": (DISCORD_PRICONNE_TWITTER_CHANNEL_ID, PRICONNE_RSS),
    "umamusume_eng": (DISCORD_UMAMUSUME_TWITTER_CHANNEL_ID, UMAMUSUME_RSS),
    # "test_channel": (DISCORD_TEST_CHANNEL_ID, PRICONNE_RSS)
}

last_tweet_ids = {}

twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER)

twitter_user_ids = {}
def get_twitter_user_id_cached(username):
    if username in twitter_user_ids:
        return twitter_user_ids[username]
    user = twitter_client.get_user(username=username)
    if user.data:
        twitter_user_ids[username] = user.data.id
        return user.data.id
    return None

twitter_target_users = [user for user, _ in TWITTER_TARGET_USERS_CHANNELS.items()]
twitter_user_index = 0

sleep_time : int = 85175

# This function checks for new tweets via Tweepy and sends them to the Discord channel.
async def check_tweets_tweepy(client: discord.Client):
    global last_tweet_ids, twitter_user_index, twitter_target_users

    await client.wait_until_ready()

    while not client.is_closed():
        try:
            user = twitter_target_users[twitter_user_index]
            channel = client.get_channel(TWITTER_TARGET_USERS_CHANNELS[user][0])
            print("Selected user:", user)
            print("Channel:", channel)

            if user not in last_tweet_ids:
                user_id = get_twitter_user_id_cached(user)
                last_tweet_ids[user] = None
            else:
                user_id = get_twitter_user_id_cached(user)

            last_id = last_tweet_ids[user]
            if last_id is None:
                tweets = twitter_client.get_users_tweets(user_id, max_results=10)
            else:
                tweets = twitter_client.get_users_tweets(user_id, max_results=5, since_id=last_id)

            if tweets.data:
                tweets_data = list(tweets.data)
                last_tweet_ids[user] = tweets_data[0].id
                
                last_discord_msgs = [msg.content async for msg in channel.history(limit=10)]
                
                for tweet in tweets_data[::-1]:
                    tweet_url = f"https://twitter.com/{user}/status/{tweet.id}"
                    if any(msg.endswith(tweet_url) for msg in last_discord_msgs):
                        print("Duplicate tweet found, skipping tweet...")
                        continue
                    tweet_translated_text = await translate_text(tweet.text)
                    tweet_translated_text = await unembed_links(tweet_translated_text)
                    await channel.send(f"{tweet_translated_text}\n{tweet_url}")

        except Exception as e:
            print("Error fetching tweets:", e)

        twitter_user_index = (twitter_user_index + 1) % len(twitter_target_users)

        await asyncio.sleep(get_sleep_time())



# This function checks for new tweets via RSS and sends them to the Discord channel.
async def check_tweets_rss(client: discord.Client):
    await client.wait_until_ready()

    while not client.is_closed():
        try:
            for user_name, (channel_id, rss_url) in TWITTER_TARGET_USERS_CHANNELS.items():
                channel = client.get_channel(channel_id)
                print("Selected user:", user_name)
                print("Channel:", channel)

                if user_name not in last_tweet_ids:
                    last_tweet_ids[user_name] = None

                feed = feedparser.parse(rss_url)
                entries = feed.entries[:10]  # take up to 10 latest

                last_discord_msgs = [msg.content async for msg in channel.history(limit=10)]

                for entry in reversed(entries):
                    tweet_url = entry.link
                    tweet_id = tweet_url.split('/')[-1]

                    if any(tweet_url in msg for msg in last_discord_msgs):
                        print("Duplicate tweet found, skipping...")
                        continue

                    print(entry)

                    content = clean_rss_content(entry)
                    translated = await translate_text(content)
                    translated = await unembed_links(translated)

                    await channel.send(f"{translated}\n{tweet_url}")

                if entries:
                    last_tweet_ids[user_name] = entries[0].link.split('/')[-1]

        except Exception as e:
            print("RSS Check Error:", e)

        await asyncio.sleep(600)

# Cleans the output from HTML tags
def clean_rss_content(entry):
    if hasattr(entry, 'summary') and entry.summary:
        raw_html = entry.summary
        
        match = re.search(r'<p[^>]*>(.*?)</p>', raw_html, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1)
        else:
            content = raw_html
            
        content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
        
        content = re.sub(r'<[^>]+>', '', content)
        
        content = html.unescape(content)
        
        return content.strip()
    
    return html.unescape(entry.title or "")

# Translates the tweet to english
async def translate_text(text):
    try:
        async with Translator() as translator:
            result = await translator.translate(text, dest='en')
            return result.text
    except Exception as e:
        print("Failed to translate given text:", e)
        return ""

async def unembed_links(text):
    if not re.search(r'https?://\S+', text):
        return text
    return re.sub(r'https?://\S+', lambda match: f"<{match.group()}>", text)

def get_sleep_time():
    global sleep_time
    sleep_time = 1215 if sleep_time == 85175 else 85175
    return sleep_time