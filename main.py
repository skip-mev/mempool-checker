import argparse
import logging
import asyncio
import aiohttp
from aiohttp_requests import requests
from collections import defaultdict
import yaml
import time
import itertools
import hashlib


def get_dict_without(d, k):
    d2 = d.copy()
    del d2[k]
    return d2

async def get_host_and_response(r):
    response = await r.json()
    return {r.host: set(response['result']['txs'])}

async def run_test(rpcs, duration):
    start = time.time()

    seen_txs = set()

    stats = defaultdict(lambda: {"unique": 0, "missed": 0})

    while time.time() - start < duration:
        tasks = [requests.get("%s/unconfirmed_txs" % rpc) for rpc in rpcs]
        reqs = await asyncio.gather(*tasks)
        time.sleep(1)

        try:
            resps = await asyncio.gather(*[get_host_and_response(r) for r in reqs])
        except aiohttp.ClientError as e:
            logging.error("Can't decode response, sleeping for 1 second: %s" % e)
            time.sleep(1)
            continue

        host_txs = {}

        for resp in resps:
            host_txs.update(resp)

        all_txs = set(itertools.chain(*host_txs.values()))
        new_txs = all_txs - seen_txs

        for host, txs in host_txs.items():
            new_host_txs = txs - seen_txs
            missed_txs = new_txs - new_host_txs
            all_txs_except_host = set(itertools.chain(*get_dict_without(host_txs, host).values())) - seen_txs
            unique_txs = new_host_txs - all_txs_except_host
        
            print("Host %s had %s txs (%s new, %s unique) and missed %d txs" % (host, len(txs), len(new_host_txs), len(unique_txs), len(missed_txs)))
            stats[host]["missed"] += len(missed_txs)
            stats[host]["unique"] += len(unique_txs)
        seen_txs.update(all_txs)
    print(yaml.dump(dict(stats), default_flow_style=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rpcs", action="append", help="RPCs to test against", required=True)
    parser.add_argument("--duration", type=int, default=60)

    args = parser.parse_args()

    if len(args.rpcs) < 2:
        logging.error("Must provide at least two RPCs")
        return
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(args.rpcs, args.duration))

        

if __name__ == "__main__":
    main()