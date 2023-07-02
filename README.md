# Simple load_testing script

## Install

`python3 -m venv venv`
`source venv/bin/activate`

`pip install -r requirements.txt`

## Run

copy websites_example.txt to websites.txt and update it to match your test urls

copy config_example.ini to config.ini and adjust your request rate

run `python3 load_test.py`

statistics will be printed and show as a graph

the test is stopped if requests are slowing down or not responded successfully or if you close the window

on close the current graph will be stored as png

## Configuration

to configure the rate of requests change the line

`asyncio.run(main(urls, Rate(100, 1), Rate(1.2, 15)))`

according to this explanation

`asyncio.run(main(urls, Rate(n, x), Rate(p, i)))`

the script performs n requests per x seconds. The rate of n is multiplied by p every i seconds

the scripts stops, of not all n requests are completed within x seconds