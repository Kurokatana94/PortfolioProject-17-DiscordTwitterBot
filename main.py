from operator import index

from dotenv import load_dotenv
from googletrans import Translator
import discord
import tweepy
import random
import asyncio
import os
import re

load_dotenv()

BOT_TOKEN=os.getenv("BOT_TOKEN")
APPLICATION_ID=os.getenv("APPLICATION_ID")
PUBLIC_KEY=os.getenv("PUBLIC_KEY")
DISCLOUD_KEY=os.getenv("DISCLOUD_KEY")
COBRA_ID=int(os.getenv("COBRA_ID"))
# KURO_ID=int(os.getenv("KURO_ID"))

DISCORD_TWITTER_CHANNEL_ID=int(os.getenv("DISCORD_TWITTER_CHANNEL_ID"))
DISCORD_TEST_CHANNEL_ID=int(os.getenv("DISCORD_TEST_CHANNEL_ID"))

TWITTER_BEARER=os.getenv("TWITTER_BEARER")
TWITTER_API_KEY=os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET=os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN=os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

TWITTER_TARGET_USER = "priconne_redive"

REPLIES_LIST = [
    "Cobra!",
    "<:kyaruStare:1293244803198226575>",
    "<:kyaruHuh:1293244809850650625> SAVE THOSE <:priconneJewel:1293244797657808896>",
    "Noooooo!",
    "Someone stop him! <:kyaruHuh:1293244809850650625>",
    "If you pull, I pull too <:kyoukaGun:1293244780419219601>",
    "Try me <:kyoukaGun:1293244780419219601>",
    "What did you just say? <:kyaruStare:1293244803198226575>",
    "https://tenor.com/oBPGwpSZCF6.gif",
    "https://tenor.com/bXz4I.gif"
]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER)

def get_twitter_user_id(username):
    user = twitter_client.get_user(username=username)
    return user.data.id if user.data else None

last_tweet_id = None
twitter_target_user_id = None

# This function checks for new tweets from the target Twitter user and sends them to the Discord channel.

async def check_tweets():
    global last_tweet_id, twitter_target_user_id

    await client.wait_until_ready()

    if twitter_target_user_id is None:
        twitter_target_user_id = get_twitter_user_id(TWITTER_TARGET_USER)

    channel = client.get_channel(DISCORD_TWITTER_CHANNEL_ID)

    while not client.is_closed():
        try:
            if last_tweet_id is None:
                tweets = twitter_client.get_users_tweets(twitter_target_user_id, max_results=5)
            else:
                tweets = twitter_client.get_users_tweets(twitter_target_user_id, max_results=5, since_id=last_tweet_id)
                print("Fetching new tweets since last tweet ID:", last_tweet_id)
            #  TODO CHECK MULTIPLE TWEETS AT ONCE (TO NOT MISS MULTIPLE TWEETS SENT IN THE 15m TIMEFRAME GIVEN BY THE API)
            if tweets.data:
                tweet = tweets.data[0]
                last_tweet_id = tweet.id
                tweet_url = f"https://twitter.com/{TWITTER_TARGET_USER}/status/{tweet.id}"
                last_discord_msg = await anext(channel.history(limit=1))
                last_discord_msg = last_discord_msg.content if last_discord_msg else ""
                if last_discord_msg.splitlines()[-1] != tweet_url:
                    tweet_translated_text = await translate_text(tweet.text)
                    tweet_translated_text = await unembed_links(tweet_translated_text)
                    await channel.send(f"{tweet_translated_text}\n{tweet_url}")
                else:
                    print("Tried to fetch new tweet, but none were found")

        except Exception as e:
            print("Error fetching tweets:", e)
        
        await asyncio.sleep(915) # Wait for 15 minutes before checking again (with an added 15s of buffering)

# async def quick_test():
#     channel = client.get_channel(DISCORD_TEST_CHANNEL_ID)
#     last_message = await anext(channel.history(limit=1))
#     await channel.send(last_message.content)

async def translate_text(text):
    try:
        async with Translator() as translator:
            result = await translator.translate(text, dest='en')
            return result.text
    except Exception as e:
        print("Failed to translate given text:", e)
        return ""

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    asyncio.create_task(check_tweets())
    # asyncio.create_task(quick_test())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author.id == COBRA_ID and find_pull(message.content):
        await message.channel.send(random.choice(REPLIES_LIST))

async def unembed_links(text):
    if not re.search(r'https?://\S+', text):
        return text
    return re.sub(r'https?://\S+', lambda match: f"<{match.group()}>", text)

def find_pull(text):
    pattern = r'(.)\1+'
    repl = r'\1'
    text = re.sub(r"[^A-Za-z ]", "", text.lower()).split()
    for word in text:
        if re.sub(pattern, repl, word) == "pul":
            return True
    return False

client.run(BOT_TOKEN)