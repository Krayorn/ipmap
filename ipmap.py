import argparse
import re
# import asyncio.subprocess
import asyncio
# import xmltodict
# import json
from aiohttp import web

def update_cache(cache, ip, res):
    cache[ip] = res

def check_cache(cache, ip):
    return ip in cache

async def scan_nmap(ip, cache):
    print("nmap -sV " + ip)
    if check_cache(cache, ip):
        print(ip, ' cached')
        result = cache[ip]
    else:
        print(ip, ' scanned')
        # '-oX', '-',,
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
        first_last_ip = to_scan.split('-')
        first_ip = first_last_ip[0]
        base_ip = first_ip.split('.')
        del base_ip[-1]
        base_ip = '.'.join(base_ip)
        start_ip = first_ip.split('.')[3]
        ip_to_reach = first_last_ip[1]
        if reg.match(first_ip):
            for i in range(int(start_ip), int(ip_to_reach)+1):
                result += await scan_nmap(str(base_ip) + '.' + str(i), cache) + "\n\n"
    else:
        result += await scan_nmap(to_scan, cache)

    # return web.Response(text=str(json.dumps(xmltodict.parse(str(result)))))
    return web.Response(text=str(result))

def main():
    cache = {}

    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

    parser = argparse.ArgumentParser()
    parser.add_argument('--port')
    parser.add_argument('--host')

    args = parser.parse_args()

    app = web.Application()
    app.router.add_get('/', lambda e: handle(e, cache))
    app.router.add_get('/{toScan}', lambda e: handle(e, cache))

    web.run_app(app, port=int(args.port), host=args.host)

main()
