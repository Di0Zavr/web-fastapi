import asyncio
from time import time

async def get_part_sum(start, end):
    return sum(range(start, end))

async def main():
    n = 1_000_000_00
    tasks_num = 10
    result = [0 for _ in range(tasks_num)]
    chunk_size = n // tasks_num

    tasks = []
    for i in range(tasks_num):
        start = i*chunk_size + 1
        end = start + chunk_size
        tasks.append(get_part_sum(start, end))
    start_time = time()

    result = await asyncio.gather(*tasks)

    total = sum(result)
    print(f"{total} - сумма")
    print(f"{time() - start_time}с. - время")

if __name__ == '__main__':
    asyncio.run(main())