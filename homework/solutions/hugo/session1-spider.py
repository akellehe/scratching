import logging
from typing import List
import aiohttp
import asyncio
import sys


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def get_callback(
    url: str,
    counter: int,
    content: str
):
    """
    The callback function that will process each URL result

    :param str url: A fully qualified URL to fetch.
    :param int counter: Which call is this? Order matters!
    :param str content: The content fetched from the URL.
    """
    logger.info(f'task {counter} callback called, {url}')


async def get_url(
    url: str = None,
    counter: int = 0,
    session: aiohttp.ClientSession = None,
    callback = None
) -> str:
    """
    Get a webpage's content, given it's URL. Uses only a simple GET HTTP Request

    :param str url: A fully qualified URL to fetch.
    :param int counter: Which call is this? Order matters!
    :param aiohttp.ClientSession session: A re-usable session for making calls.
    :param callback: A function reference to call once we get a response.

    :return: str The result.
    """
    if session is None:
        raise ValueError('`session` is a required argument. You must pass an HTTP Session')
    logger.info(f'task {counter} awaiting, {url}')
    result = await session.get(url)
    logger.info(f'task {counter} returned, {url}')

    if (callback):
      callback(url, counter, result)

    return await result.text()


async def spider(
    urls: List[str],
    session : aiohttp.ClientSession = None,
    callback = None
):
    """
    Manage the list of tasks

    :param List[str] urls: A list of URLs to process.
    :param aiohttp.ClientSession session: A re-usable session for making calls.
    :param callback: A function reference to call once we get a response.
    """
    if session is None:
        raise ValueError('`session` is a required argument. You must pass an HTTP Session')

    # which URL index are we at
    counter = 0
    # the number of tasks we'll be running concurrently
    max_running_tasks = 10
    # the set of tasks we are gowing to run
    tasks = set()

    # while we have new URLs to process
    while counter < len(urls):
        # if we have 10 or more tasks waiting, wait for a task to complete
        if len(tasks) >= max_running_tasks:
            _done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        # if we have fewer than 10 tasks running, add another task for the next URL
        tasks.add(asyncio.create_task(get_url(urls[counter], counter, session, callback)))
        logger.info(f'created task {counter}, {urls[counter]}')
        # increase the URL index
        counter += 1

    # wait for the remaining tasks to complete
    await asyncio.wait(tasks)


async def main():
    # list of URLs
    urls = [
        'https://staging.titfortat.io',
        'https://google.com/',
        'https://sapo.pt/',
        'https://duckduckgo.com/']
    # duplicate list of URLs two times, 16 in total
    for _ in range(0, 2):
        urls.extend(urls)

    print(f'Will process {len(urls)} URLs')

    # wait for the spider method to complete,
    # pass the callback function to call for each URL result
    async with aiohttp.ClientSession() as session:
        await spider(urls, session, get_callback)


if __name__ == '__main__':
    asyncio.run(main())
