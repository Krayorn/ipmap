import argparse
import re
import asyncio
from aiohttp import web
# this two were used to return json
# import xmltodict
# import json

def update_cache(cache, ip, res):
    cache[ip] = res

def check_cache(cache, ip):
    return ip in cache

async def scan_nmap(ip, cache):
    print("nmap -sV " + ip)

    # if ip already in cache, just print it
    if check_cache(cache, ip):
        print(ip, ' cached')
        result = cache[ip]
    else:
    #if not, make an nmap, and then add it to the cache
        print(ip, ' scanned')
        # '-oX', '-', send xml instead of txt
        process = await asyncio.create_subprocess_exec(
            'nmap', '-sV', ip,
            stdout=asyncio.subprocess.PIPE)

        stdout, _ = await process.communicate()
        result = stdout.decode().strip()
        update_cache(cache, ip, result)

    return result

async def handle(request, cache):
    to_scan = request.match_info.get('toScan', "192.168.1.0")

    result = ''
    reg = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    if '-' in to_scan:

        # parse ip, get all the base, the first ip to check, and the last
        first_last_ip = to_scan.split('-')
        first_ip = first_last_ip[0]
        base_ip = first_ip.split('.')
        del base_ip[-1]
        base_ip = '.'.join(base_ip)
        start_ip = first_ip.split('.')[3]
        ip_to_reach = first_last_ip[1]

        if reg.match(first_ip):
            for i in range(int(start_ip), int(ip_to_reach)+1):
                # make nmap for each ip from the range
                result += await scan_nmap(str(base_ip) + '.' + str(i), cache) + "\n\n"
    else:
        result += await scan_nmap(to_scan, cache)

    # was used for json aswell
    # return web.Response(text=str(json.dumps(xmltodict.parse(str(result)))))
    return web.Response(text=str(result))

def main():
    cache = {}

    # used on windows machine, won't work properly with mac
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

    # allow you to use custom port and host for the server ex: python.exe ipmap.py --port=8080 --host=127.0.0.1
    parser = argparse.ArgumentParser()
    parser.add_argument('--port')
    parser.add_argument('--host')

    args = parser.parse_args()

    app = web.Application()

    # lambda are used to pass the cache to the handle
    app.router.add_get('/', lambda e: handle(e, cache))
    app.router.add_get('/{toScan}', lambda e: handle(e, cache))

    web.run_app(app, port=int(args.port), host=args.host)

main()
