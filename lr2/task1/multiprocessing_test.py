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