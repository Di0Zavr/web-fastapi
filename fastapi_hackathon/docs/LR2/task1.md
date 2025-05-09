# Сравнение подходов параллелизма на CPU нагрузке

## Реализация

В качестве теста был выбран метод суммирования чисел от 1 до 100.000.000. Для сравнения был произведён замер времени.

Для сравнения были выбраны подходы мультипоточности с помощью библиотеки threading, мультипроцессинга из библиотеки multiprocessing и асинхронности с помощью библиотеки asyncio.

С мультипоточностью мы используем общую память, поэтому был заведён список в который потоки записывали свою частичную сумму. После этого просто просуммировали частичные суммы.

```python
from threading import Thread
from time import time

def get_part_sum(start, end, result, index):
    result[index] = sum(range(start, end))

if __name__ == '__main__':
    n = 1_000_000_00
    threads_num = 10
    result = [0 for _ in range(threads_num)]
    chunk_size = n // threads_num

    threads = []
    start_time = time()
    for i in range(threads_num):
        start = i*chunk_size + 1
        end = start + chunk_size
        t = Thread(target=get_part_sum, args=(start, end, result, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total = sum(result)
    print(f"{total} - сумма")
    print(f"{time() - start_time}с. - время")
```

С мультипроцессингом мы создаём пул процессов, каждый из которых считаем свою сумму и возвращает её. После этого мы собираем все результаты и суммируем.

```python
from multiprocessing import Pool
from time import time

def get_part_sum(start, end):
    return sum(range(start, end))

if __name__ == '__main__':
    n = 1_000_000_00
    process_num = 10
    chunk_size = n // process_num
    p = Pool(process_num)

    payloads = []
    for i in range(process_num):
        start = i*chunk_size + 1
        end = start + chunk_size
        payloads.append((start, end))

    start_time = time()
    result = p.starmap(get_part_sum, payloads)

    total = sum(result)
    print(f"{total} - сумма")
    print(f"{time() - start_time}с. - время")
```

С асинхронностью также возвращаем из функи частичную сумму и в конце собираем их.

```python
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
```

## Сравнение

Здесь представлена сравнительная таблица.

| single thread | threading | multiprocessing | asyncio |
|---------------|-----------|-----------------|---------|
|    6.503с.    | 7.665с.   | 3.016с.         | 6.659с. |

Мультипроцессинг показал ускорение времени вычислений по сравнению с двумя другими подходами. Это связано с тем, что в данном случае у нас CPU-bound нагрузка и асинхронность не ускоряет вычисления, а потоки блокируются GIL из-за того что они используют общую память. Процессы используют раздельную память и поэтому они могут работать параллельно.
