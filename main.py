from dotenv import load_dotenv
from googletrans import Translator
import feedparser
import discord
import random
import asyncio
import html
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

# TWITTER_BEARER=os.getenv("TWITTER_BEARER")
# TWITTER_API_KEY=os.getenv("TWITTER_API_KEY")
# TWITTER_API_SECRET=os.getenv("TWITTER_API_SECRET")
# TWITTER_ACCESS_TOKEN=os.getenv("TWITTER_ACCESS_TOKEN")
# TWITTER_ACCESS_TOKEN_SECRET=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

PRICONNE_RSS = os.getenv("PRICONNE_RSS")
UMAMUSUME_RSS = os.getenv("UMAMUSUME_RSS")

TWITTER_TARGET_USERS_CHANNELS = {
    "priconne_redive": (DISCORD_PRICONNE_TWITTER_CHANNEL_ID, PRICONNE_RSS),
    "umamusume_eng": (DISCORD_UMAMUSUME_TWITTER_CHANNEL_ID, UMAMUSUME_RSS),
    # "test_channel": (DISCORD_TEST_CHANNEL_ID, PRICONNE_RSS)
}

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

last_tweet_ids = {}

# This function checks for new tweets via RSS and sends them to the Discord channel.
async def check_tweets():
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

# Translates the tweet to english
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

# Sends a funny message in response to a give trigger from a specific user
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

client.run(BOT_TOKEN)