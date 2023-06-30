# Simple load_testing script

## Install

`python3 -m venv venv`
`source venv/bin/activate`

`pip install -r requirements.txt`

## Run

simply run `python3 load_test.py`


## Configuration

to configure the rate of requests change the line

`asyncio.run(main(urls, Rate(100, 1), Rate(1.2, 15)))`

according to this explanation

`asyncio.run(main(urls, Rate(n, x), Rate(p, i)))`

the script performs n requests per x seconds. The rate of n is multiplied by p every i seconds
the scripts stops, of not all n requests are completed within x seconds