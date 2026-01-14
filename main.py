from dotenv import load_dotenv
import packages.twitter_feed as twitter_feed
import aiohttp
import discord
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

LLM_API_URL = os.getenv("LLM_API_URL")

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

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    asyncio.create_task(twitter_feed.check_tweets_tweepy(client))

# TODO ON EVENT IF USER WRITES  "@" + APPLICATION_ID OR USES THE NAME KAT OR ANGYKAT, THEN SEND A REQUEST TO GENERATE A RESPONSE WITH THE LLM USING AN API
# Sends a funny message in response to a give trigger from a specific user
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author.id == COBRA_ID and find_pull(message.content):
        await message.channel.send(random.choice(REPLIES_LIST))

    # Example message <Message id=1460424691641618515 channel=<TextChannel id=1395438988277321859 name='bot-testing' position=7 nsfw=False news=False category_id=1091723593915842700> type=<MessageType.default: 0> author=<Member id=263726038381494272 name='kurokatana94' global_name='Kuro' bot=False nick=None guild=<Guild id=1091723593446068336 name='Ashes of Astrum' shard_id=0 chunked=False member_count=27>> flags=<MessageFlags value=0>>
    # Example message content <:kyaruSurprise:1293244808365871185> edited <@1394484064651710614>
    if message.author.global_name == "Kuro" and message.channel.name == "bot-testing":
        await send_llm_request(message)
    elif client.user.mentioned_in(message) | any(word in message.content.lower() for word in ["kat", "angykat", "angy kat"]) | is_replied_to(message):
        await send_llm_request(message)

async def send_llm_request(message):
    print(message)
    print(message.content)
    async with aiohttp.ClientSession() as session:
        payload = {
            "user_input": message.content,
            "username": message.author.global_name,
        }
        try:
            async with session.post(LLM_API_URL, json=payload, timeout=60) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await message.channel.send(data["response"])
                else:
                    print(f"Error: Received status code {resp.status}")
                    await message.reply(random.choice(["zzz...zzz...", "D-don't bother me...", "Five more minutes... zzz..."]))
        except Exception as e:
            await message.reply(f"I don't feel so good... (Request Error: {e}).")

def is_replied_to(message):
    ref = message.reference
    if not ref:
        return False
    
    target = ref.cached_message or ref.resolved
    
    if target and hasattr(target, 'author'):
        return target.author.id == client.user.id
        
    return False

def find_pull(text):
    pattern = r'(.)\1+'
    repl = r'\1'
    text = re.sub(r"[^A-Za-z ]", "", text.lower()).split()
    for word in text:
        if re.sub(pattern, repl, word) in TRIGGER_WORDS:
            return True
    return False

client.run(BOT_TOKEN)