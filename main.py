import requests
import json
from bs4 import BeautifulSoup
import os
import time


# text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
headers = requests.utils.default_headers()

headers = {
    "accept": "application/json, text/plain, */*",
    # "Referer": "https://landingfolio.com/templates",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

def get():
    url = f"https://landingfolio.com/api/template?page=1&sortBy=free-first"
    
    r = requests.get(url=url, headers=headers)
    data = r.json()
    for item in data:
        print(item.get("title"))
    try:
        with open("result_list.json", "a") as file:
            json.dump(r.json(), file, indent=4, ensure_ascii=False)
    except Exception as ex:
        print("json write error: ", ex)

"""Collectinlg data and return a json file"""
def get_data_file():
    page = 1
    img_count = 0
    result_data = []

    for page in range(1, 11):
        url = f"https://landingfolio.com/api/template?page={page}&sortBy=free-first"

        try:
            response = requests.get(url=url, headers=headers)
        except Exception as ex:
            print(f" error request {page}", ex)
            continue

        data = response.json()
        for item in data:
            images = item.get("images")
            img_count += len(images)

            img = {
                "desktop": "https://landingfoliocom.imgix.net/" + images.get("desktop"),
                "mobile": "https://landingfoliocom.imgix.net/" + images.get("mobile")
            }
                    
            result_data.append(
                {
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "url": item.get("previewUrl"),
                    "images": img
                }
            )

        print(f"[+] Processed {page}")
        page += 1

    with open("result_list2.json", "w") as file:
        json.dump(result_data, file, indent=4, ensure_ascii=False)

    print(f"[INFO] Work finished. Images count is: {img_count}\n{'n' * 20}")


def download_imgs(file_path):
    
    try:
        with open(file_path) as file:
            src = json.load(file)
    except Exception as ex:
        print(ex)
        return "[INFO] Check the file path"

    item_len = len(src)
    count = 1

    for item in src[:10]:
        item_name = item.get("title")
        item_imgs = item.get("images")

        if not os.path.exists(f"data/{item_name}"):
            os.mkdir(f"data/{item_name}")
        
        r = requests.get(url=item_imgs["desktop"])

        with open(f"data/{item_name}/desktop.png", "wb") as file:
            file.write(r.content)

        r = requests.get(url=item_imgs["mobile"])

        with open(f"data/{item_name}/mobile.png", "wb") as file:
            file.write(r.content)

        print(f"[+] Download {count}/{item_len}")
        count += 1

    return "[INFO] Work finished!"

def main():
    # get_data_file()
    start_time = time.time()

    get()
    # print(download_imgs("result_list2.json"))

    finish_time = time.time() - start_time
    print(f"Worked time: {finish_time}")

if __name__ == '__main__':
    main()

# https://landingfolio.com/api/template?page=2&sortBy=free-first