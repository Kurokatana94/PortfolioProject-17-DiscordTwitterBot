from dotenv import load_dotenv
import packages.twitter_feed as twitter_feed
from packages.emotes_formatter import format_response, format_user_input
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

COBRA_TRIGGER_WORDS = [
    "pul",
    "puls",
    "pulz",
]

GENERAL_TRIGGER_WORDS = [
    "kat ",
    " kat",
    " kat ",
    " angykat",
    "angykat ",
    " angykat ",
    " angy",
    "angy ",
    " angy ",
    ]

TRIGGER_RE = re.compile(r'(?<![\/\.])\b(kat|angykat|angy)\b', re.IGNORECASE)

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

    context = await extract_latest_messages(message.channel)

    # Example message <Message id=1460424691641618515 channel=<TextChannel id=1395438988277321859 name='bot-testing' position=7 nsfw=False news=False category_id=1091723593915842700> type=<MessageType.default: 0> author=<Member id=263726038381494272 name='kurokatana94' global_name='Kuro' bot=False nick=None guild=<Guild id=1091723593446068336 name='Ashes of Astrum' shard_id=0 chunked=False member_count=27>> flags=<MessageFlags value=0>>
    # Example message content <:kyaruSurprise:1293244808365871185> edited <@1394484064651710614>
    if message.author.global_name in ["Kuro", "Hori"] and message.channel.name == "bot-testing":
        await send_llm_request(message, context)
    elif message.author.id == COBRA_ID and find_pull(message.content):
        await send_llm_request(message, context)
    elif client.user.mentioned_in(message) or bool(is_replied_to(message)) or bool(TRIGGER_RE.search(message.content)):
        await send_llm_request(message, context)
    # elif TRIGGER_RE.search(message.content):
    #     await send_llm_request(message) if random.random() < 0.8 else None
    # else:
    #     context = await extract_latest_messages(message.channel)
    #     reply_required = await send_response_evaluation_request(context)
    #     if reply_required:
    #         await send_llm_request(message, context)
    

async def send_llm_request(message, context=None):
    print(message)
    print(message.content)
    print(message.author)
    async with aiohttp.ClientSession() as session:
        user_input = format_user_input(message.clean_content)
        username = message.author.global_name or message.author.display_name or message.author.name
        request_context = [{"user_input": msg.clean_content, "username": msg.author.global_name or msg.author.display_name or msg.author.name} for msg in reversed(context)] if context else []
        request_context = [msg for msg in request_context if isinstance(msg, dict)]

        print(f"Sending request to LLM API with user_input: {user_input}, \nusername: {username}, \nrequest_context: {request_context}")

        payload = {
            "user_input": user_input,
            "username": username,
            "request_context": request_context
        }
        try:
            async with session.post(f"{LLM_API_URL}/chat", json=payload, timeout=20) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await message.channel.send(format_response(data["response"]))
                else:
                    print(f"Error: Received status code {resp.status}")
                    
                    if message.author.id == COBRA_ID and find_pull(message.content):
                        await message.channel.send(random.choice(REPLIES_LIST))
                    else:
                        await message.reply(random.choice(["zzz...zzz...", "D-don't bother me...", "Five more minutes... zzz..."]))
                    
        except Exception as e:
            print("Request error:", e)
            await message.reply(f"I don't feel so good... Tell Kuro my tummy hurts!")

# async def send_response_evaluation_request(context):
#     print("Evaluating context for response...")
#     print([msg.content for msg in context])
#     async with aiohttp.ClientSession() as session:
#         payload = {
#             "request_context": [msg.clean_content for msg in context]
#         }
#         try:
#             async with session.post(f"{LLM_API_URL}/evaluate", json=payload, timeout=20) as resp:
#                 if resp.status == 200:
#                     data = await resp.json()
#                     return data["should_respond"]
#                 else:
#                     print(f"Error: Received status code {resp.status} during evaluation")
#                     return False
#         except Exception as e:
#             print("Evaluation request error:", e)
#             return False

async def extract_latest_messages(channel, limit=10):
    messages = []
    async for message in channel.history(limit=limit):
        messages.append(message)
    return messages

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
        if re.sub(pattern, repl, word) in COBRA_TRIGGER_WORDS:
            return True
    return False

client.run(BOT_TOKEN)