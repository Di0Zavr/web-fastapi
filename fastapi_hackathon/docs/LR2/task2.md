# Сравнение подходов параллелизма на I/O нагрузке

## Реализация

Для теста потребовалось собрать данные с нескольких сайтов и загрузить их в базу данных. Для этого были написаны функции для получения адресов, выгрузки данных и преобразование их в формат для базы данных

```python
import requests
import random
import string
import aiohttp
from models import *
from db import get_session, get_async_session
from bs4 import BeautifulSoup
from datetime import datetime

# парсим хакатоны.рус
HOST = "https://feeds.tildacdn.com"  # сайт сделан на тильде и данные подтягиваются из апи тильды
LIST_API_ENDPOINT = "/api/getfeed/?feeduid=617755803461&recid=488755787&c={timestamp}&size={size}&slice={slice}"
SIZE = 20
SLICE = 1
USER_AGENT = "".join(random.choices(string.ascii_letters, k=20))
SESSION = requests.session()
SESSION.headers["User-Agent"] = USER_AGENT

def get_urls(size=SIZE, slice=SLICE):
    now_timestamp = int(datetime.timestamp(datetime.now()) * 1000)
    url = HOST + LIST_API_ENDPOINT.format(timestamp=now_timestamp, size=size, slice=slice)
    hackathons_list = SESSION.get(url).json()["posts"]
    urls = [post["url"] for post in hackathons_list if "tpost" in post["url"]]
    return urls

async def async_get_urls(size=SIZE, slice=SLICE):
    session = aiohttp.ClientSession()
    now_timestamp = int(datetime.timestamp(datetime.now()) * 1000)
    url = HOST + LIST_API_ENDPOINT.format(timestamp=now_timestamp, size=size, slice=slice)
    response = await session.get(url)
    json_data = await response.json()
    await session.close()
    hackathons_list = json_data["posts"]
    urls = [post["url"] for post in hackathons_list if "tpost" in post["url"]]
    return urls

def _fetch_data(url):
    r = SESSION.get(url, headers={"User-Agent": USER_AGENT})
    return r.text, r.status_code

async def _async_fetch_data(url):
    timeout = aiohttp.ClientTimeout(10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers={"User-Agent": USER_AGENT}) as response:
            response.raise_for_status()
            return await response.text(), response.status

def _parse_html(data):
    soup = BeautifulSoup(data, "html.parser")
    dto = {
        "title": None,
        "description": None,
        "participant_conditions": None,
        "location": None,
        "dates": None,
        "organizer_id": 18  # тестовый юзер
    }
    dto["title"] = soup.find("h1", attrs={"class": "js-feed-post-title t-feed__post-popup__title t-title t-title_xxs"}).text.strip()
    descr = soup.find("div", attrs={"class": "t-redactor__tte-view"})
    descr_blocks = descr.find_all("div")
    description = ""
    for block in descr_blocks:
        if "Дата проведения" in block.text:
            dto["dates"] = block.text.split("Дата проведения")[1].split('\n')[0].strip()
        if "Место проведения" in block.text:
            dto["location"] = block.text.split("Место проведения:")[1].split('\n')[0].strip()
        if "Регистрация до" in block.text:
            break
        description += block.text + '\n'
    dto["description"] = description
    if not dto["location"]:
        dto["location"] = "Онлайн"
    
    return dto

def _load_in_db(dto):
    session = next(get_session())
    data = HackathonDefault(
        name=dto["title"],
        description=dto["description"],
        participant_conditions=dto["participant_conditions"],
        location=dto["location"],
        dates=dto["dates"],
        organizer_id=dto["organizer_id"]
    )
    model = Hackathon.model_validate(data)
    session.add(model)
    session.commit()
    session.refresh(model)

def fetch_parse_load(url):
    data, status = _fetch_data(url)
    if status == 404:
        return False
    data = _parse_html(data)
    _load_in_db(data)
    return True

async def async_fetch_parse_load(url):
    data, status = await _async_fetch_data(url)
    if status == 404:
        return False
    data = _parse_html(data)
    _load_in_db(data)
    return True
```

C помощью этих функций был произведён тест разных подходов

Мультипоточность:

```python
import threading
from time import time
from parser import fetch_parse_load, get_urls

SIZE = 10
SLICE = 3

def parse_and_load(url):
    if fetch_parse_load(url):
        print(f"{url} - finished!")
    else:
        print(f"{url} - failed!")

def main():
    urls = get_urls(SIZE, SLICE)
    threads = []
    start_time = time()

    for url in urls:
        # print(f"{url} - loading...")
        t = threading.Thread(target=parse_and_load, args=(url,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    
    print(f"{time() - start_time}с. - время")

if __name__ == '__main__':
    main()

```

Мультипроцессность:

```python
from multiprocessing import Pool
from time import time
from parser import fetch_parse_load, get_urls

SIZE = 10
SLICE = 4

def parse_and_load(url):
    if fetch_parse_load(url):
        print(f"{url} - finished!")
    else:
        print(f"{url} - failed!")

def main():
    urls = get_urls(SIZE, SLICE)
    p = Pool(10)
    start_time = time()

    p.map(parse_and_load, urls)
    
    print(f"{time() - start_time}с. - время")

if __name__ == '__main__':
    main()

```

Асинхронность

```python
import asyncio
from time import time
from parser import async_get_urls, async_fetch_parse_load

SIZE = 10
SLICE = 5

async def parse_and_load(url):
    if await async_fetch_parse_load(url):
        print(f"{url} - finished!")
    else:
        print(f"{url} - failed!")

async def main():
    urls = await async_get_urls(SIZE, SLICE)
    tasks = []
    start_time = time()

    for url in urls:
        tasks.append(parse_and_load(url))

    await asyncio.gather(*tasks, return_exceptions=True)
    
    print(f"{time() - start_time}с. - время")

if __name__ == '__main__':
    asyncio.run(main())

```

Наконец, стандартный тест в один поток:

```python
import threading
from time import time
from parser import fetch_parse_load, get_urls

SIZE = 10
SLICE = 6

def parse_and_load(url):
    if fetch_parse_load(url):
        print(f"{url} - finished!")
    else:
        print(f"{url} - failed!")

def main():
    urls = get_urls(SIZE, SLICE)
    start_time = time()

    for url in urls:
        parse_and_load(url)
    
    print(f"{time() - start_time}с. - время")

if __name__ == '__main__':
    main()

```

## Сравнение

Здесь представлена сравнительная таблица разных подходов

| single thread | threading | multiprocessing | async   |
|---------------|-----------|-----------------|---------|
| 3.416c.       | 1.163с.   | 11.712с.        | 1.405с. |

Мультипоточность и асинхронность показали хороший результат при I/O-bound нагрузки. В свою очередь, мультипроценность показала результат хуже одного потока из-за затрат на создании процессов и отсутствии выйгрыша при нескольких процессах.
