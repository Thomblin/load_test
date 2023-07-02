import asyncio
import time
from typing import List, Tuple
from Rate import Rate

import aiohttp
from debug import print_error, print_info
from draw import InterimResult, create_graph, update_graph
import config as config

async def get(url: str, session: aiohttp.ClientSession):
    try:
        async with session.get(url=url) as response:
            start_time = time.time()
            await response.read()
            end_time = time.time()

            if response.status != 200:
                raise Exception(f"response code = {response.status}")
            
            return end_time-start_time
    except Exception as e:
        print_error(f"Unable to get url {url} : {e}")

def rotate_urls(urls: List[str], n: int) -> Tuple[List[str], List[str]]:
    if n > len(urls):
        repetitions = (n // len(urls)) + 1
        tmp = urls * repetitions
        tmp = tmp[:n]
    else:
        tmp = urls[:n]
        urls[:] = urls[n:]
        urls.extend(tmp[:n])

    return tmp, urls

async def crawl(request_urls):
    async with aiohttp.ClientSession() as session:
            latency = await asyncio.gather(*[get(url, session) for url in request_urls])
    return latency

def main(urls: List[str], rate: Rate, acceleration: Rate, allowed_failures=5):

    intervall_start = time.time()
    count_delay = 0
    
    graph = create_graph()

    while True:
        start_time = time.time()
        
        request_urls, urls = rotate_urls(urls, int(rate.magnitude))

        print_info(f"batch {len(request_urls)} @ {start_time} {rate}")

        latency = asyncio.run(crawl(request_urls))
        
        update_graph(graph, InterimResult(start_time, latency, rate))

        sleep = rate.window - (time.time() - start_time)
        if sleep > 0:
            print_info(f"sleep {sleep}")
            time.sleep(sleep)
            if count_delay > 0:
                count_delay -= 1
        else:
            count_delay += 1
            print_error("requests are slower than rate")

        if count_delay > allowed_failures:
            return
        
        if time.time() - intervall_start  > acceleration.window:     
            rate.magnitude *= acceleration.magnitude
            intervall_start = time.time()
            count_delay = 0
            print_info(f"increased rate to {rate}")

with open('websites.txt', 'r') as file:
    urls = file.read().split("\n")

cfg_rate = config.load_section('rate')
cfg_acceleration = config.load_section('acceleration')
cfg_failures = config.load_section('failures')

main(
    urls, 
    Rate(float(cfg_rate['magnitude']), float(cfg_rate['window'])), 
    Rate(float(cfg_acceleration['magnitude']), float(cfg_acceleration['window'])), 
    int(cfg_failures['allowed'])
)