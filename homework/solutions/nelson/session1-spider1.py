from asyncio.futures import Future
from asyncio.tasks import sleep
import logging
from typing import List
import asyncio
import sys

import aiohttp
from typing_extensions import IntVar

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

async def get(url: str = None, counter: int = 0, callback = None, session: aiohttp.ClientSession = None) -> str:
    """
    Get a webpage's content, given it's URL. Uses only a simple GET HTTP Request

    :param str url: A fully qualified URL to fetch.
    :param int counter: Which call is this? Order matters!
    :param aiohttp.ClientSession session: A re-usable session for making calls.

    :return: str The result.
    """
    if session is None:
        raise ValueError('`session` is a required argument. You must pass an HTTP Session')
    logger.info(f'Awaiting {url} in call {counter}.')
    result = await session.get(url)
    if callback:
        callback(url, counter, await result.text())
    return await result.text()

def get_using_task(url: str, counter: int, callback = None, session : aiohttp.ClientSession = None) -> asyncio.Task:
    if session is None:
        raise ValueError('`session` is a required argument. You must pass an HTTP Session')

    mycoroutine = get(url, counter, callback, session)
    return asyncio.create_task(mycoroutine)

async def spider(urls: List[str], concurrency: int = 1, callback = None, session : aiohttp.ClientSession = None):
    if session is None:
        raise ValueError('`session` is a required argument. You must pass an HTTP Session')

    complete_tasks = set()
    pending_tasks = set()

    for counter, url in enumerate(urls):
        logger.info(f'Spider[{counter+1}]: {url}')

        # adds new task per each iteration
        pending_tasks.add(get_using_task(url, counter=counter+1, callback=callback, session=session))
        logger.info(f'Adding tasks => pending_tasks: {len(pending_tasks)}')

        # pendings_tasks already reached the max value (concurrency), executes the tasks and waits for the next one to complete
        if len(pending_tasks) >= concurrency:
            logger.info('Executing tasks...')
            done, pending_tasks = await asyncio.wait(pending_tasks, return_when=asyncio.FIRST_COMPLETED)
            complete_tasks.update(done)
            logger.info(f'Executing tasks => completed_tasks={len(done)} pending_tasks={len(pending_tasks)}')

        # Last iteration: complete ALL the remaining pending_tasks (if existent)
        if counter == len(urls)-1 and len(pending_tasks) > 0:
            logger.info('Executing all the remaining tasks...')
            done, pending_tasks = await asyncio.wait(pending_tasks, return_when=asyncio.ALL_COMPLETED)
            complete_tasks.update(done)
            logger.info(f'Executing all the remaining tasks => completed_tasks={len(done)} pending_tasks={len(pending_tasks)}')

def httpCallback(url: str, counter: int, result: str):
    logger.info(f'REQUEST  => {url} was returned in the {counter} call.')
    logger.info(f'RESPONSE => {result}')

async def main():
    logger.info('')
    logger.info('-------------------------------------------')
    logger.info('WebSpider with limited parallel concurrency')
    logger.info('-------------------------------------------')

    """
    # URL base list
    urls = ['http://api.tvmaze.com/search/shows?q=girls', 'http://api.tvmaze.com/search/shows?q=cars', 'http://api.tvmaze.com/search/shows?q=rock', 'http://api.tvmaze.com/search/shows?q=roll', 'http://api.tvmaze.com/search/shows?q=adrenaline']    
    urlsExtended = []
    for _ in range(0, 20):
        urlsExtended.extend(urls)
    """

    # Note: to use with local node server (each requests takes 5s to respond)
    # > node index.js
    # > time curl "http://localhost:8080/?count=1"
    urlsExtended = []
    for count in range(1,25+1):
        urlsExtended.extend([f'http://localhost:8080/count={count}'])

    # set the concurrency level
    concurrency = 10

    async with aiohttp.ClientSession() as session:
        await spider(urlsExtended, concurrency, httpCallback, session)

    logger.info('-------------------------------------------')


if __name__ == '__main__':
    asyncio.run(main())
