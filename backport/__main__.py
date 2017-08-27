import asyncio
import os
import sys
import traceback

import aiohttp
from aiohttp import web
import cachetools
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing
from gidgethub import sansio

from . import backport_pr


router = routing.Router(backport_pr.router)
cache = cachetools.LRUCache(maxsize=500)

import subprocess


async def main(request):
    try:
        body = await request.read()
        print(os.listdir('.'))
        # if not os.path.isdir("cpython"):
        #     print("cloning")
        #     result = subprocess.check_output("git clone https://github.com/mariatta/cpython.git".split())
        #
        #     print(result.decode('utf-8'))
        os.chdir('cpython')
        # print(os.listdir('.'))
        print(subprocess.check_output("git remote --v".split()).decode('utf-8'))
        # result = subprocess.check_output("git remote add upstream https://github.com/mariatta/cpython.git".split())
        # print(result.decode('utf-8'))
        # print(subprocess.check_output("git remote --v".split()).decode('utf-8'))
        # print("done check output")
        # print(subprocess.check_output("git log 8ccc723920ee001fea48f5ede8b721c7f96f473d".split()).decode('utf-8'))
        os.chdir('..')

        secret = os.environ.get("GH_SECRET")
        print(request.headers)
        event = sansio.Event.from_http(request.headers, body, secret=secret)
        print('GH delivery ID', event.delivery_id, file=sys.stderr)
        if event.event == "ping":
            return web.Response(status=200)
        oauth_token = os.environ.get("GH_AUTH")
        async with aiohttp.ClientSession() as session:
            gh = gh_aiohttp.GitHubAPI(session, "mariatta/cpython",
                                      oauth_token=oauth_token,
                                      cache=cache)
            # Give GitHub some time to reach internal consistency.
            await asyncio.sleep(1)
            await router.dispatch(event, gh)
        return web.Response(status=200)
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        return web.Response(status=500)

def clone_cpython():
    """ Clone CPython, and set upstream remote"""
    if not os.path.isdir("cpython"):
        print("cloning")
        result = subprocess.check_output(
            "git clone https://github.com/mariatta/cpython.git".split())

        print(result.decode('utf-8'))

        result = subprocess.check_output("git remote add upstream https://github.com/mariatta/cpython.git".split())
        print(result.decode('utf-8'))

if __name__ == "__main__":  # pragma: no cover
    clone_cpython()
    app = web.Application()
    app.router.add_post("/", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)
    web.run_app(app, port=port)


