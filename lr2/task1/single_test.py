from time import time

def get_sum(start, end):
    return sum(range(start, end))

if __name__ == '__main__':
    n = 1_000_000_00
    start_time = time()
    total = get_sum(1, n + 1)

    print(f"{total} - сумма")
    print(f"{time() - start_time}с. - время")