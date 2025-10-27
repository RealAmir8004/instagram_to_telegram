import msvcrt
import os
import asyncio
from telegram import Bot
from telegram.error import RetryAfter, TimedOut
import instaloader
from config import BOT_TOKEN, CHAT_ID
import sys

INPUT = "URL_inputs.txt"
SENT_LOG = "sent_videos.log"
DOWNLOAD_LOG = "downloaded_urls.log"
FOLDER = "dowloaded_from_insta"

class MainController:
    def __init__(self):
        if not os.path.exists(INPUT):
            print(f"Error: {INPUT} file not found! Please create it with one URL per line.")
            open(INPUT, "w", encoding="utf-8").close()
        self.urls = self.generate_static_url()
        self.D = instaloader.Instaloader(dirname_pattern="{target}", save_metadata=False, download_comments=False)
        # self.D.login('realamir8004')
        self.bot = Bot(token=BOT_TOKEN)
        self.sent_videos = self.load_sent_videos()
        self.downloaded_urls = self.load_downloaded_urls()

    def generate_static_url(self):
        urls =[]
        with open(INPUT,  "r", encoding="utf-8") as f:
            for line in f :
                url = line.strip()
                if '/reel/' in url:
                    urls.append(url.split('?')[0])
        return urls

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
            print(f"Failed to download url →it may be deleted={url}   : '{e}'")
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
        retry_count = 0
        max_retries = 2
        
        while not sent and retry_count < max_retries:
            try:
                print(f"Uploading {filename}... (Attempt {retry_count + 1}/{max_retries})")
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
                retry_count += 1
            except TimedOut:
                print("Error: Timed out")
                await asyncio.sleep(10)
                retry_count += 1
            except Exception as e:
                print(f"Error: {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"Failed to send {filename} after {max_retries} attempts. Skipping...")
                await asyncio.sleep(10)
        
        if not sent:
            print(f"Giving up on {filename} after {max_retries} failed attempts")


    def run(self , mode):
        if mode == 1 or mode == 2:
            for url in self.urls:
                self.download_from_insta(url)
            if not self.urls:
                print(f"{INPUT} file was empty")

        if mode == 1 or mode == 3:
            async def send_all_videos():
                for video_path in [os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.endswith('.mp4')]:
                    await self.send_to_telegram(video_path)
            
            # Run all videos in a single event loop
            asyncio.run(send_all_videos())


def menu_choose():
    print("Choose mode:")
    print("[1] Download & Send")
    print("[2] Download only")
    print("[3] Send only")
    print("[4] force re-download previous links (clear download log )")
    print("[5] force re-send previous downloadeds (clear sent log )")
    print("[6] Cancel & exit")
    while True:
        print("\nPlease enter 1, 2, 3, 4, 5, or 6: ", end='', flush=True)
        key = msvcrt.getch()
        if key == b'1':
            print('1')
            return 1
        elif key == b'2':
            print('2')
            return 2
        elif key == b'3':
            print('3')
            return 3
        elif key == b'4':
            print('4')
            open(DOWNLOAD_LOG, "w", encoding="utf-8").close()
            print("cleared download log successfully")
        elif key == b'5':
            print('5')
            open(SENT_LOG, "w", encoding="utf-8").close()
            print("cleared sent log successfully")
        elif key == b'6':
            print('6')
            sys.exit()

if __name__ == "__main__":
    controller = MainController()
    controller.run(menu_choose())