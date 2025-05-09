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