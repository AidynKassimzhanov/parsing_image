import requests
import json
from bs4 import BeautifulSoup
import os
import time
import asyncio
import aiohttp


headers = requests.utils.default_headers()

headers = {
    "accept": "application/json, text/plain, */*",
    # "Referer": "https://landingfolio.com/templates",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}


async def download_images(session, url, file_path, count):
    async with session.get(url=url, headers=headers) as response:
        content = await response.read()
        if content:
            with open(file_path, "wb") as file:
                file.write(content)
            print(f"[+] Download {count} /{file_path}")



async def gather_data(file_path):
    async with aiohttp.ClientSession() as session:
        try:
            with open(file_path) as file:
                src = json.load(file)
        except Exception as ex:
            print(ex)
            return "[INFO] Check the file path"

        tasks = []

        item_len = len(src)
        count = 1

        for item in src[:5]:
            item_name = item.get("title")
            item_imgs = item.get("images")

            if not os.path.exists(f"data/{item_name}"):
                os.mkdir(f"data/{item_name}")

            url = item_imgs["desktop"]
            file_path = f"data/{item_name}/desktop.png"
            task = asyncio.create_task(download_images(session, url, file_path, count))
            tasks.append(task)

            url = item_imgs["mobile"]
            file_path = f"data/{item_name}/mobile.png"
            task = asyncio.create_task(download_images(session, url, file_path, count))
            tasks.append(task)

            count += 1
            await asyncio.sleep(0.05)
        
        await asyncio.gather(*tasks)
    
    return "[INFO] Work finished!"


def main():
    start_time = time.time()

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(gather_data("result_list2.json"))
    # asyncio.run(gather_data("result_list2.json"))

    finish_time = time.time() - start_time
    print(f"Worked time: {finish_time}")


if __name__ == '__main__':
    main()
