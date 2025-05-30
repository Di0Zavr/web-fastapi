import asyncio
from fastapi import FastAPI
from task2.parser import async_get_urls, async_fetch_parse_load

app = FastAPI()

@app.post("/parse")
async def parse(size: int=10, slice: int=1):
    urls = await async_get_urls(size, slice)
    tasks = []

    for url in urls:
        tasks.append(async_fetch_parse_load(url))

    await asyncio.gather(*tasks, return_exceptions=True)
    return {"ok": True}

