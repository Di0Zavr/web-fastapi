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
