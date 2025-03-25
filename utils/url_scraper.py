"""
    This file is a utility to scrape a seed url 
    and find all sub-links recursively, until all 
    specified link types have been found.
    Ot then saves the relevant urls into a txt file to
    be used later for parsing content
"""
import asyncio
import aiohttp
import urllib.parse
from selenium import webdriver
from bs4 import BeautifulSoup

main_queue = asyncio.Queue()
parsed_links_queue = asyncio.Queue()
parsed_links = set()

session = None
f_out = None
visited_urls = 0

async def get_url(url):
    global visited_urls
    try:
        async with session.get(url) as resp:
            visited_urls += 1
            return await resp.text()
    except:
        print(f"Bad URL: {url}")

async def worker():
    driver = webdriver.Chrome()
    while True:
        url = await main_queue.get()
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for a in soup.select("a[href]"):
            href = a["href"]
            if href.startswith(("/hc/en-gb/categories/", "/hc/en-gb/sections/", "/hc/en-gb/articles/")) and ":" not in href:
                parsed_links_queue.put_nowait("https://joinvoy.zendesk.com" + href)
        main_queue.task_done()

async def consumer():
    while True:
        url = await parsed_links_queue.get()
        if url not in parsed_links:
            if "/hc/en-gb/articles/" in url:
                print(urllib.parse.unquote(url), file=f_out, flush=True)  # <-- print the url to file
            parsed_links.add(url)
            main_queue.put_nowait(url)

        parsed_links_queue.task_done()


async def main():
    global session, f_out

    seed_url = "https://joinvoy.zendesk.com/hc/en-gb"
    parsed_links.add(seed_url)

    with open("./outputs/parsed_urls.txt", "w") as f_out:
        async with aiohttp.ClientSession() as session:
            workers = {asyncio.create_task(worker()) for _ in range(16)}
            c = asyncio.create_task(consumer())

            main_queue.put_nowait(seed_url)
            print("Initializing...")
            await asyncio.sleep(5)

            while main_queue.qsize():
                print(f"Visited URLs: {visited_urls:>7}  Known URLs (saved in parsed_urls.txt): {len(parsed_links):>7}", flush=True)
                await asyncio.sleep(0.1)

    await main_queue.join()
    await parsed_links_queue.join()

asyncio.run(main())