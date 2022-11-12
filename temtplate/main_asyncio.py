import json
import csv
import time
import datetime
import requests
from bs4 import BeautifulSoup

import asyncio
import aiohttp


headers = requests.utils.default_headers()
headers.update(
    {
        "accept": "text/html, */*; q=0.01",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }
)


books_data = []
start_time = time.time()

async def get_page_data(session, page):
    url = f"https://www.labirint.ru/genres/2308/?available=1&paperbooks=1&display=table&page={page}&histlab=5886296362"
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, "lxml")

        books_items = soup.find("tbody", class_="products-table__body").find_all("tr")
        
        # book_data = books_items[0].find_all("td")
        # print(book_data[0].find("a").text)

        for bi in books_items:
            book_data = bi.find_all("td")

            try:
                book_title = book_data[0].find("a").text.strip()
            except:
                book_title = "Нет названия книги"

            try:
                book_author = book_data[1].text.strip()
            except:
                book_author = "Нет автора"

            try:
                # book_publishing = book_data[2].text
                book_publishing = book_data[2].find_all("a")
                book_publishing = ":".join([bp.text for bp in book_publishing])
            except:
                book_publishing = "Нет издательства"

            try:
                book_new_price = int(book_data[3].find("div", class_="price").find("span").find("span").text.strip().replace(" ", ""))
            except:
                book_new_price = "Нет нового прайса"

            try:
                book_old_price = int(book_data[3].find("span", class_="price-gray").text.strip().replace(" ", ""))
            except:
                book_old_price = "Нет старого прайса"

            try:
                book_sale = round(((book_old_price - book_new_price) / book_old_price) * 100)
            except:
                book_sale = "Нет скидки"

            try:
                book_status = book_data[-1].text.strip()
            except:
                book_status = "Нет статуса"

            books_data.append(
                {
                    "book_title": book_title,
                    "book_author": book_author,
                    "book_publishing": book_publishing,
                    "book_new_price": book_new_price,
                    "book_old_price": book_old_price,
                    "book_sale": book_sale,
                    "book_status": book_status
                }
            )

        print(f"[INFO] Обработал страницу {page}")


async def gather_data():
    async with aiohttp.ClientSession() as session:
        url = f"https://www.labirint.ru/genres/2308/?available=1&paperbooks=1&display=table&page=1"
        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), "lxml")
        pages_count = int(soup.find("div", class_="pagination-numbers__right").find_all("a")[-1].text)

        tasks = []

        for page in range(1, pages_count + 1):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # vasyncio.run(main())
    asyncio.run(gather_data())
    cur_time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")

    with open(f"labirint_{cur_time}_asunc.json", "w", encoding="utf-8", newline="") as file:
        json.dump(books_data, file, indent=4, ensure_ascii=False)

    with open(f"labirint_{cur_time}.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                "Название книги",
                "Автор",
                "Издательство",
                "Цена со скидкой",
                "Цена без скидки",
                "Процент скидки",
                "Наличие на складе"
            )
        )

    for book in books_data:
        
        with open(f"labirint_{cur_time}_async.csv", "a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)

            writer.writerow(
                (
                    book["book_title"],
                    book["book_author"],
                    book["book_publishing"],
                    book["book_new_price"],
                    book["book_old_price"],
                    book["book_sale"],
                    book["book_status"]
                )
            )

    finish_time = time.time() - start_time
    print(f"Затраченное на работу скрипта время: {finish_time}")

if __name__ == '__main__':
    main()