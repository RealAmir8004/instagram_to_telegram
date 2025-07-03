import os
import asyncio
from telegram import Bot
from telegram.error import RetryAfter, TimedOut
import instaloader

INPUT = "inputs_URL.txt"
FOLDER = "dowloaded_from_insta"
BOT_TOKEN = '7348207324:AAFps7dQ-SJHlXTrrXSlBLf1OVfGblfDegw'
CHAT_ID = XXXXXX  
SENT_LOG = "sent_videos.txt"
DOWNLOAD_LOG = "downloaded_urls.txt"

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
            print(f"{SENT_LOG} does not exist. Returning empty set.")
            return set()
        with open(SENT_LOG, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)

    def save_sent_video(self, filename):
        with open(SENT_LOG, "a", encoding="utf-8") as f:
            f.write(filename + "\n")

    def load_downloaded_urls(self):
        if not os.path.exists(DOWNLOAD_LOG):
            print(f"{DOWNLOAD_LOG} does not exist. Returning empty set.")
            return set()
        with open(DOWNLOAD_LOG, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)

    def save_downloaded_url(self, url):
        with open(DOWNLOAD_LOG, "a", encoding="utf-8") as f:
            f.write(url + "\n")

    def download_from_insta(self, url):
        shortcode = url.rstrip("/").split("/")[-1]
        # Search for mp4 files in FOLDER that contain the shortcode
        if url in self.downloaded_urls:
            print(f"URL already downloaded: {url}")
            mp4_files = [f for f in os.listdir(FOLDER) if f.endswith('.mp4') and shortcode in f]
            print(f"Found {len(mp4_files)} mp4 files for shortcode {shortcode} in {FOLDER}")
            return [os.path.join(FOLDER, f) for f in mp4_files]
        try:
            print(f"Downloading post for shortcode: {shortcode}")
            self.D.dirname_pattern = FOLDER
            self.D.download_post(instaloader.Post.from_shortcode(self.D.context, shortcode), target=shortcode)
            # After download, search for mp4 files in FOLDER that contain the shortcode
            mp4_files = [f for f in os.listdir(FOLDER) if f.endswith('.mp4') and shortcode in f]
            print(f"Downloaded {len(mp4_files)} mp4 files for shortcode {shortcode} in {FOLDER}")
            self.save_downloaded_url(url)
            return [os.path.join(FOLDER, f) for f in mp4_files]
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return []

    async def run(self):
        for url in self.urls:
            mp4_files = self.download_from_insta(url)
            if not mp4_files:
                print(f"continue loop :No mp4 files found for {url}")
                continue

        for video_path in [os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.endswith('.mp4')]:
            filename = os.path.basename(video_path)
            if filename not in self.sent_videos:
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
                        sent = True  # Skip this file after error

if __name__ == "__main__":
    contoller = MainController()
    asyncio.run(contoller.run())