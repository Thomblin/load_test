import asyncio
from dataclasses import dataclass
import time
from typing import List, Tuple, NewType
import statistics

import aiohttp
import numpy as np

websites = """http://127.0.0.1/
http://127.0.0.1/page1
http://127.0.0.1/page2
"""

NORMAL = None
RED = "\033[91m"
GREEN = "\033[92m"
END_COLOR = "\033[0m"

Seconds = NewType("Seconds", float)

@dataclass
class Rate:
    magnitude: float = 1.0
    window: Seconds = 60.0

def print_color(text: str, color: str):
    if color is None:
        print(text)
    else:
        print(f"{color}{text}{END_COLOR}")

async def get(url: str, session: aiohttp.ClientSession):
    try:
        async with session.get(url=url) as response:
            start_time = time.time()
            resp = await response.read()
            end_time = time.time()

            if response.status != 200:
                raise Exception(f"response code = {response.status}")
            
            return end_time-start_time
    except Exception as e:
        print_color(f"Unable to get url {url} : {e}", RED)

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

async def main(urls: List[str], rate: Rate, acceleration: Rate, allowed_failures=5):

    intervall_start = time.time()
    last_average = 1.0
    last_percentile_10 = 1.0
    count_delay = 0
    while True:
        start_time = time.time()
        
        request_urls, urls = rotate_urls(urls, int(rate.magnitude))

        print(f"batch {len(request_urls)} @ {start_time} {rate}")

        async with aiohttp.ClientSession() as session:
            latency = await asyncio.gather(*[get(url, session) for url in request_urls])

            lost_requests = len(list(filter(lambda x: x is None, latency)))
            cleaned_latency = list(filter(lambda x: x is not None, latency))
            average = statistics.mean(cleaned_latency)
            percentile_10 = np.percentile(cleaned_latency, 10)

            if last_average < average or last_percentile_10 < percentile_10 or lost_requests > len(cleaned_latency):
                color = RED
            else:
                color = GREEN
            print_color(f"avg: {average} 10Q: {percentile_10} lost_requests: {lost_requests}", color)

        sleep = rate.window - (time.time() - start_time)
        if sleep > 0:
            print(f"sleep {sleep}")
            time.sleep(sleep)
            if count_delay > 0:
                count_delay -= 1
        else:
            count_delay += 1
            print_color("requests are slower than rate", RED)

        if count_delay > allowed_failures:
            return
        
        if time.time() - intervall_start  > acceleration.window:     
            rate.magnitude *= acceleration.magnitude
            intervall_start = time.time()
            count_delay = 0
            print(f"increased rate to {rate}")

urls = websites.split("\n")
asyncio.run(main(urls, Rate(10, 1), Rate(1.33, 15), 10))