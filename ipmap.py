import argparse
import asyncio.subprocess
import asyncio
from aiohttp import web

async def get_Nmap(to_scan):
    print("nmap -sV " + to_scan)

    process = await asyncio.create_subprocess_exec(
        'nmap', '-sV', to_scan,
        stdout=asyncio.subprocess.PIPE)

    stdout, stderr = await process.communicate()

    result = stdout.decode().strip()
    return result


async def handle(request):
    to_scan = request.match_info.get('toScan', "192.168.1.0")

    result = await get_Nmap(to_scan)
    return web.Response(text=str(result))

def main():
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

    parser = argparse.ArgumentParser()
    parser.add_argument('--port')
    parser.add_argument('--host')

    args = parser.parse_args()

    app = web.Application()
    app.router.add_get('/', handle)
    app.router.add_get('/{toScan}', handle)

    web.run_app(app, port=int(args.port), host=args.host)

main()
