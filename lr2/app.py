import asyncio
from fastapi import FastAPI, HTTPException
from task2.parser import async_get_urls, async_fetch_parse_load
from worker.worker import parse_url, celery_app

app = FastAPI()

@app.post("/parse")
async def parse(size: int=10, slice: int=1):
    urls = await async_get_urls(size, slice)
    tasks = []

    for url in urls:
        tasks.append(async_fetch_parse_load(url))

    await asyncio.gather(*tasks, return_exceptions=True)
    return {"ok": True}

@app.post("/parse_celery")
async def parse_celery(size: int=10, slice: int=1):
    urls = await async_get_urls(size, slice)
    ids = []
    for url in urls:
        task = parse_url.delay(url)
        ids.append(task.id)
    return {"id": ids}

@app.post("/parse_url")
async def parse_celery_single_url(url: str):
    task = parse_url.delay(url)
    return {"id": task.id}

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    res = celery_app.AsyncResult(task_id)
    if res.state == "FAILURE":
        raise HTTPException(500, detail=str(res.result))
    return {"state": res.state}
