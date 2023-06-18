import aiohttp
import asyncio
import time

start_time = time.time()


async def get_url(session, url):
    async with session.get(url, headers={"Access-Token": "test"}) as resp:
        status = resp.status
        try:
            res = await resp.json()
            return res
        except:
            return status


async def main():

    async with aiohttp.ClientSession() as session:

        tasks = []
        for number in range(5):
            url = f'http://localhost:80'
            tasks.append(asyncio.ensure_future(get_url(session, url)))

        statuses = await asyncio.gather(*tasks)
        for status in statuses:
            print(status)

asyncio.run(main())
print("--- %s seconds ---" % (time.time() - start_time))
