import asyncio
import threading
import sys
import math
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from download import run_downloading
import time

audio_url = ""
url = ""
timeout = 10000
progress_thread = None
progress_running = False


def progress(count, total, status='', bar_len=50):
    bar = '=' * int(count * bar_len / total) + '-' * \
        (bar_len - int(count * bar_len / total))
    sys.stdout.write(f'[{bar}] {round(100 * count / total, 1)}% - {status}\r')
    sys.stdout.flush()


def run_progress():
    global progress_running
    for i in range(0, math.floor(timeout / 1000)):
        if not progress_running:
            break
        progress(i + 1, math.floor(timeout / 1000), 'Getting audio details')
        time.sleep(1)


async def main():
    global progress_running
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        async def log_request(request):
            global audio_url
            if "mp3" in request.url or "m4a" in request.url:
                audio_url = request.url

        page = await context.new_page()
        page.on("request", log_request)

        global progress_thread
        progress_running = True
        progress_thread = threading.Thread(target=run_progress)
        progress_thread.start()

        try:
            await page.goto(url, timeout=timeout)
            print("Page loaded")
        except Exception as e:
            pass
        finally:
            progress_running = False
            progress_thread.join()

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        run_downloading(audio_url,
                        soup.select_one('.cover')['src'], soup.select_one('.cover')['title'])
        await browser.close()


if __name__ == '__main__':
    print("""
  _____         __  ___             ___                  __             __       
 / ___/__ ____ / /_/ _ )___ __ __  / _ \___ _    _____  / /__  ___ ____/ /__ ____
/ /__/ _ `(_-</ __/ _  / _ \\\ \ / / // / _ \ |/|/ / _ \/ / _ \/ _ `/ _  / -_) __/
\___/\_,_/___/\__/____/\___/_\_\ /____/\___/__,__/_//_/_/\___/\_,_/\_,_/\__/_/   
""")
    url = input('Enter the castbox link (episode link): ')
    timeout = input("Enter timeout limit in ms (or type default): ")
    if timeout.lower() == 'default':
        timeout = 10000
    else:
        timeout = int(timeout)
    asyncio.run(main())
