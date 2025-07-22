# Discord Twitter Bot
A lightweight Discord bot that monitors a specific Twitter user's activity and shares new tweets to a Discord channel in real time. Built with **Tweepy** and **discord.py**, this project is perfect for communities wanting to stay updated on a user’s posts without needing to check Twitter manually.

## Concept
- Monitors a specific Twitter account for new tweets.
- Automatically posts new tweets into a designated Discord channel.
- Avoids duplicates by checking the latest message in the channel.
- Optionally translates tweet text before posting (multi-language support).
- Respects Twitter’s Free Tier API rate limits. (one call every 15 minutes)

## Built With
- [**Tweepy**](https://docs.tweepy.org/en/stable/) – for Twitter API integration
- [**discord.py**](https://discordpy.readthedocs.io/en/stable/) – for interacting with Discord servers and channels
- [**googletrans**](https://pypi.org/project/googletrans/) – for translating the tweets text content
- **aiohttp / asyncio** – for asynchronous execution
- **dotenv** – for environment variable management

## Features
- Tracks new tweets using Twitter’s v2 API
- Prevents reposting already-shared tweets
- Detects tweet links in the last message in the channel
- Optional real-time translation via googletrans
- Scheduled fetch with configurable interval (defaults to 15 minutes)

## Controls & Setup
- **No user interaction required** once running — the bot operates on a timer.
- Setup involves:
  1. Creating a `.env` file in your project folder to store private tokens
  2. Providing your Discord bot token and Twitter API keys
  3. Setting your target username and Discord channel ID
  4. Launching the bot from your compiler or a hosted environment

### Extra
- [Discloud](https://discloud.com/) – for hosting the bot service at low prices (with free tier available)
- [Discord Developer Portal](https://discord.com/developers/applications) – to manage your bots and invites/permissions

### Thanks for Checking It Out!
Feel free to **download**, **modify**, and **use** this project however you'd like. Feedback or suggestions are always welcome!

