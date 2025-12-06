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

DISCORD_PRICONNE_TWITTER_CHANNEL_ID=int(os.getenv("DISCORD_PRICONNE_TWITTER_CHANNEL_ID"))
DISCORD_UMAMUSUME_TWITTER_CHANNEL_ID=int(os.getenv("DISCORD_UMAMUSUME_TWITTER_CHANNEL_ID"))
DISCORD_TEST_CHANNEL_ID=int(os.getenv("DISCORD_TEST_CHANNEL_ID"))

TWITTER_BEARER=os.getenv("TWITTER_BEARER")
TWITTER_API_KEY=os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET=os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN=os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

TWITTER_TARGET_USERS_CHANNELS = {"priconne_redive":DISCORD_PRICONNE_TWITTER_CHANNEL_ID, "umamusume_eng":DISCORD_UMAMUSUME_TWITTER_CHANNEL_ID}

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

TRIGGER_WORDS = [
    "pul",
    "puls",
    "pulz",
]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

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

last_tweet_ids = {}
twitter_target_users = [user for user, _ in TWITTER_TARGET_USERS_CHANNELS.items()]
twitter_user_index = 0

sleep_time : int = 85175

# This function checks for new tweets from the target Twitter user and sends them to the Discord channel.

async def check_tweets():
    global last_tweet_ids, twitter_user_index, twitter_target_users

    await client.wait_until_ready()

    while not client.is_closed():
        try:
            user = twitter_target_users[twitter_user_index]
            channel = client.get_channel(TWITTER_TARGET_USERS_CHANNELS[user]) # client.get_channel(DISCORD_TEST_CHANNEL_ID) # <-- for testing
            print("Selected user:", user)
            print("Channel:", channel)

            if user not in last_tweet_ids:
                user_id = get_twitter_user_id_cached(user)
                last_tweet_ids[user] = None
            else:
                user_id = get_twitter_user_id_cached(user)
            # print("Last tweet ID:", last_tweet_ids)
            # print("Selected user ID:", user_id)
            last_id = last_tweet_ids[user]
            if last_id is None:
                tweets = twitter_client.get_users_tweets(user_id, max_results=10)
                # print("Fetching tweets 'ID None':", tweets)
            else:
                tweets = twitter_client.get_users_tweets(user_id, max_results=10, since_id=last_id)
                print("Fetching new tweets since last tweet ID:", last_id)

            # Checks for the latest discord messages and sends translated if no doubles
            if tweets.data:
                tweets_data = list(tweets.data)
                last_tweet_ids[user] = tweets_data[0].id
                
                last_discord_msg = await anext(channel.history(limit=1), None)
                last_discord_msg = last_discord_msg.content if last_discord_msg else " "
                
                for tweet in tweets_data[::-1]:
                    tweet_url = f"https://twitter.com/{user}/status/{tweet.id}"

                    if last_discord_msg.splitlines()[-1] != tweet_url:
                        tweet_translated_text = await translate_text(tweet.text)
                        tweet_translated_text = await unembed_links(tweet_translated_text)
                        await channel.send(f"{tweet_translated_text}\n{tweet_url}")
                    else:
                        print("Tried to fetch new tweet, but none were found")

        except Exception as e:
            print("Error fetching tweets:", e)

        twitter_user_index = (twitter_user_index + 1) % len(twitter_target_users)

        await asyncio.sleep(1215) # Wait for 4h 48m before checking again (with an added 15s of buffering) <-- I need to increase it to few hours to maybe once a day... stupid twitter limit | 86400 (24h) get_sleep_time()

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
        if re.sub(pattern, repl, word) in TRIGGER_WORDS:
            return True
    return False

def get_sleep_time() -> int:
    global sleep_time
    sleep_time = 1215 if sleep_time == 85175 else 85175
    return sleep_time

client.run(BOT_TOKEN)