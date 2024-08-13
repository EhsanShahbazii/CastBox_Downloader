import asyncio
import aiohttp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2
import nest_asyncio
import os

nest_asyncio.apply()


async def download(session, url, path):
    async with session.get(url) as response:
        response.raise_for_status()
        with open(path, 'wb') as file:
            while True:
                chunk = await response.content.read(8192)
                if not chunk:
                    break
                file.write(chunk)


async def download_mp3(audio_url, image_url, filename):
    f_name = filename + '.m4a'
    async with aiohttp.ClientSession() as session:
        try:
            await asyncio.gather(
                download(session, audio_url, f_name),
                download(session, image_url, filename + '.jpg')
            )

            if not os.path.exists(f_name) or os.path.getsize(f_name) == 0:
                print("Downloaded MP3 file is missing or empty.")
                return

            audio = MP3(f_name, ID3=ID3)
            audio.tags.add(TIT2(encoding=3, text=filename))
            audio.save()
        except Exception as e:
            print(f"\nDownload complete --> {f_name}")


def run_downloading(audio_url, image_url, filename):
    asyncio.run(download_mp3(audio_url, image_url, filename))
