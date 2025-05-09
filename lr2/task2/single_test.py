import threading
from time import time
from parser import fetch_parse_load, get_urls

SIZE = 10
SLICE = 6

def parse_and_load(url):
    if fetch_parse_load(url):
        print(f"{url} - finished!")
    else:
        print(f"{url} - failed!")

def main():
    urls = get_urls(SIZE, SLICE)
    start_time = time()

    for url in urls:
        parse_and_load(url)
    
    print(f"{time() - start_time}с. - время")

if __name__ == '__main__':
    main()
