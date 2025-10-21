import os
import asyncio
from telegram import Bot
from telegram.error import RetryAfter, TimedOut
import instaloader
from config import BOT_TOKEN, CHAT_ID

INPUT = "URL_inputs.txt"
SENT_LOG = "sent_videos_log.txt"
DOWNLOAD_LOG = "downloaded_urls_log.txt"
FOLDER = "dowloaded_from_insta"

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


    def run(self , mode):
if mode == 1 or mode == 2:
        for url in self.urls:
            self.download_from_insta(url)
if not self.urls:
                print(f"{INPUT} file was empty")

if mode == 1 or mode == 3:
        for video_path in [os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.endswith('.mp4')]:
            asyncio.run(self.send_to_telegram(video_path))


def menu_choose():
    print("Choose mode:")
    print("[1] Download & Send")
    print("[2] Download only")
    print("[3] Send only")
    print("[4] force re-download previous links (clear download log )")
    print("[5] force re-send previous downloadeds (clear sent log )")
    while True:
        print("\nPlease enter 1, 2, 3, 4, or 5: ", end='', flush=True)
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

if __name__ == "__main__":
    controller = MainController()
    controller.run(menu_choose())