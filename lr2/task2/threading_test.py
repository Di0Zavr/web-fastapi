import threading
from time import time
from parser import fetch_parse_load, get_urls

SIZE = 10
SLICE = 3

def parse_and_load(url):
    if fetch_parse_load(url):
        print(f"{url} - finished!")
    else:
        print(f"{url} - failed!")

def main():
    urls = get_urls(SIZE, SLICE)
    threads = []
    start_time = time()

    for url in urls:
        # print(f"{url} - loading...")
        t = threading.Thread(target=parse_and_load, args=(url,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    
    print(f"{time() - start_time}с. - время")

if __name__ == '__main__':
    main()
