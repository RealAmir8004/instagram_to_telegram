# Instagram to Telegram Video Transfer Bot
This bot automatically downloads Instagram reels and uploads them to Telegram chat (with description of video attached).

## Features
- Downloads Instagram reels to local storage
- Forwards videos to Telegram with captions of the video as caption of massage
- Maintains logs to prevent duplicate downloads/uploads

## Required Python packages
   - telegram-bot 
   - instaloader

## Setup & Usage

1. Configure your Chat ID:
   1. Start a chat with [@ASVWC_BOT](https://t.me/ASVWC_BOT) on Telegram
   2. Send any message to the bot
   3. Visit: `https://api.telegram.org/bot7348207324:AAFps7dQ-SJHlXTrrXSlBLf1OVfGblfDegw/getUpdates`
   4. Look for your Chat ID in `"chat":{"id":XXXXXXXX}`
   5. Open `config.py` and update the `CHAT_ID` value with yours


2. Add Instagram reel URLs to `URL_inputs.txt`, one per line
   ```
   https://www.instagram.com/reel/ABC123xyz/
   https://www.instagram.com/reel/XYZ789abc/
   ```
   Note: Only use "static" URLs without query parameters:
   - ✓ `https://www.instagram.com/reel/ABC123xyz/`
   - ✖ `https://www.instagram.com/reel/ABC123xyz/?utm_source=ig_web_copy_link`

3. Run : download&send.py

4. 
   - for download & send (default use):
      enter 1
   - To only download without sending to Telegram:
      enter 2
   - To only send existing videos without downloading:
      enter 3
   - To force re-download previous links (clear download log ):
      enter 4
   - To force re-send previous downloadeds (clear sent log ):
      enter 5

## Advanced Usage
we can change the bot if needed 
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use the `/newbot` command to create a new bot
3. Copy the bot token provided
4. replace `BOT_TOKEN` and use `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` 

## File Structure
- `download&send.py`: Main bot script
- `URL_inputs.txt`: List of Instagram URLs to process
- `downloaded_urls.log`: Tracks downloaded URLs
- `sent_videos.log`: Tracks sent videos
- `dowloaded_from_insta/`: Storage for downloaded videos
