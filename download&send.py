import os
import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.error import RetryAfter, TimedOut
import instaloader
import re

SENT_LOG = "sent_videos_log.txt"
DOWNLOAD_LOG = "downloaded_urls_log.txt"
FOLDER = "dowloaded_from_insta"
BOT_TOKEN = '7348207324:AAFps7dQ-SJHlXTrrXSlBLf1OVfGblfDegw'

class InstagramBot:
    def __init__(self):
        self.D = instaloader.Instaloader(dirname_pattern="{target}", save_metadata=False, download_comments=False)
        # self.D.login('realamir8004')  # Uncomment if login needed
        os.makedirs(FOLDER, exist_ok=True)
        self.sent_videos = self.load_sent_videos()
        self.downloaded_urls = self.load_downloaded_urls()

    def load_sent_videos(self):
        if not os.path.exists(SENT_LOG):
            return set()
        with open(SENT_LOG, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)

    def save_sent_video(self, filename):
        with open(SENT_LOG, "a", encoding="utf-8") as f:
            f.write(filename + "\n")

    def load_downloaded_urls(self):
        if not os.path.exists(DOWNLOAD_LOG):
            return set()
        with open(DOWNLOAD_LOG, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)

    def save_downloaded_url(self, url):
        with open(DOWNLOAD_LOG, "a", encoding="utf-8") as f:
            f.write(url + "\n")

    async def download_from_insta(self, url):
        if url in self.downloaded_urls:
            return True, "This reel has already been downloaded."
        try:
            shortcode = url.rstrip("/").split("/")[-1]
            self.D.dirname_pattern = FOLDER
            self.D.download_post(instaloader.Post.from_shortcode(self.D.context, shortcode), target=shortcode)
            self.save_downloaded_url(url)
            return True, f"Successfully downloaded reel: {shortcode}"
        except Exception as e:
            return False, f"Failed to download: {str(e)}"

    async def send_to_telegram(self, video_path, chat_id):
        filename = os.path.basename(video_path)
        if filename in self.sent_videos:
            return "This video has already been sent."
        
        base_name = filename[:-4]
        txt_path = os.path.join(FOLDER, base_name + '.txt')
        caption = ''
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                caption = f.read()

        sent = False
        while not sent:
            try:
                with open(video_path, 'rb') as video_file:
                    await bot.send_video(
                        chat_id=chat_id,
                        video=video_file,
                        caption=caption[:1024],
                    )
                self.save_sent_video(filename)
                sent = True
                await asyncio.sleep(5)
                return "Video sent successfully!"
            except RetryAfter as e:
                await asyncio.sleep(e.retry_after)
            except TimedOut:
                await asyncio.sleep(10)
            except Exception as e:
                return f"Error sending video: {str(e)}"

    async def process_instagram_url(self, url, chat_id):
        success, message = await self.download_from_insta(url)
        if not success:
            return message
        
        # Find the downloaded video file
        shortcode = url.rstrip("/").split("/")[-1]
        video_files = [f for f in os.listdir(FOLDER) if f.startswith(shortcode) and f.endswith('.mp4')]
        if not video_files:
            return "Downloaded but couldn't find the video file."
        
        video_path = os.path.join(FOLDER, video_files[0])
        return await self.send_to_telegram(video_path, chat_id)

bot = None
instagram_bot = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! Send me Instagram reel links and I'll download and forward them to you.\n\n"
        "The link should be (static) like this format:\n"
        "✅ https://www.instagram.com/reel/abc123xyz/\n"
        "not this:\n"
        "❌ https://www.instagram.com/reel/abc123xyz/?utm_source=ig_web_copy_link"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "How to use this bot:\n\n"
        "1. Send an Instagram reel link\n"
        "2. Wait while I download and process it\n"
        "3. I'll send you the video!\n\n"
        "Note: Links must be (static) like this format:\n"
        "https://www.instagram.com/reel/[code]/"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    # Check if the message contains an Instagram reel URL
    match = re.search(r'https?://(?:www\.)?instagram\.com/reel/([^/?]+)', text)
    
    if not match:
        await update.message.reply_text(
            "Please send a valid (static) Instagram reel link.\n"
            "Example: https://www.instagram.com/reel/abc123xyz/"
        )
        return

    status_message = await update.message.reply_text("Processing your request...")
    result = await instagram_bot.process_instagram_url(match.group(0), update.message.chat_id)
    await status_message.edit_text(result)

def main():
    global bot, instagram_bot
    
    # Initialize the Instagram bot
    instagram_bot = InstagramBot()
    
    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()