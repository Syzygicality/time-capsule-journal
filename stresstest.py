import asyncio
import httpx
import time

URL = "https://journal.edisonwang.dev/" # manually set API endpoint
CONCURRENCY = int(input("Concurrency: "))
TOTAL_REQUESTS = int(input("Total Requests: "))

async def fetch(client):
    resp = await client.get(URL)
    return resp.status_code

async def main():
    async with httpx.AsyncClient() as client:
        tasks = []
        start = time.time()
        for _ in range(TOTAL_REQUESTS):
            tasks.append(fetch(client))
            if len(tasks) >= CONCURRENCY:
                results = await asyncio.gather(*tasks)
                tasks = []
        if tasks:
            results = await asyncio.gather(*tasks)
        elapsed = time.time() - start
        rps = TOTAL_REQUESTS / elapsed
        print(f"Total time: {elapsed:.2f}s")
        print(f"Requests per second: {rps:.2f} req/sec")
        print(f"Requests per minute: {rps * 60:.2f} req/min")

asyncio.run(main())