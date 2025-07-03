import os
import asyncio
from telegram import Bot
from telegram.error import RetryAfter, TimedOut
import instaloader

INPUT = "URL_inputs.txt"
SENT_LOG = "sent_videos_log.txt"
DOWNLOAD_LOG = "downloaded_urls_log.txt"
FOLDER = "dowloaded_from_insta"
BOT_TOKEN = '7348207324:AAFps7dQ-SJHlXTrrXSlBLf1OVfGblfDegw'
CHAT_ID = XXXXXX  
# CHAT_ID can discover by"https://api.telegram.org/bot7348207324:AAFps7dQ-SJHlXTrrXSlBLf1OVfGblfDegw/getUpdates" or other methodes

class MainController:
    def __init__(self):
        with open(INPUT, "r", encoding="utf-8") as f:
            self.urls = [line.strip() for line in f if line.strip()]
        self.D = instaloader.Instaloader(dirname_pattern="{target}", save_metadata=False, download_comments=False)
        # self.D.login('realamir8004')
        self.bot = Bot(token=BOT_TOKEN)
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

    def download_from_insta(self, url):
        if url in self.downloaded_urls:
            print(f"files already downloaded for url={url}")
            return True
        try:
            print(f"Downloading post for url: {url}")
            shortcode = url.rstrip("/").split("/")[-1]
            self.D.dirname_pattern = FOLDER
            self.D.download_post(instaloader.Post.from_shortcode(self.D.context, shortcode), target=shortcode)
            self.save_downloaded_url(url)
            print(f"Downloaded files for url={url}")
            return True
        except Exception as e:
            print(f"Failed to download url={url}   : {e}")
            return False

    async def send_to_telegram(self , video_path):
        filename = os.path.basename(video_path)
        if filename in self.sent_videos:
            print(f"already sented file={filename}")
            return
        base_name = filename[:-4]
        txt_path = os.path.join(FOLDER, base_name + '.txt')
        caption = ''
        if os.path.exists(txt_path):
            print(f"Loading caption from {txt_path}")
            with open(txt_path, 'r', encoding='utf-8') as f:
                caption = f.read()
        print(f"Sending: {filename} to tel id : {CHAT_ID}")
        sent = False
        while not sent:
            try:
                with open(video_path, 'rb') as video_file:
                    print(f"Uploading {filename}...")
                    await self.bot.send_video(
                        chat_id=CHAT_ID,
                        video=video_file,
                        caption=caption[:1024],
                    )
                self.save_sent_video(filename)
                print(f"Sent and logged: {filename}")
                sent = True
                await asyncio.sleep(5)
            except RetryAfter as e:
                print(f"Flood control: waiting {e.retry_after} seconds")
                await asyncio.sleep(e.retry_after)
            except TimedOut:
                print("Error: Timed out")
                await asyncio.sleep(10)
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(10)
                sent = True # ignore and skip 


    def run(self):
        for url in self.urls:
            self.download_from_insta(url)

        for video_path in [os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.endswith('.mp4')]:
            asyncio.run(self.send_to_telegram(video_path))


if __name__ == "__main__":
    contoller = MainController()
    contoller.run()