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
