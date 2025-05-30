import requests
import random
import string
import aiohttp
from .models import *
from .db import get_session
from bs4 import BeautifulSoup
from datetime import datetime

# парсим хакатоны.рус
# всего записей 934 поэтому мы ограничены в ресурсах
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
        "organizer_id": 1  # тестовый юзер
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
