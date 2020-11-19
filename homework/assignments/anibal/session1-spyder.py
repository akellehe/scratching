import logging
from typing import List
import asyncio
import sys

import aiohttp
import datetime


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

URL = 'https://staging.titfortat.io'


async def get(url: str = None, counter: int = 0, session: aiohttp.ClientSession = None) -> str:
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
    logger.info(f'{url} was returned in the {counter} call.')
    return await result.text()



async def get_many_using_gather(urls: List[str], session: aiohttp.ClientSession = None) -> List[str]:
    """
    Get several pages CONCURRENTLY, given a list of URLs.

    :param list<str> urls: A list of URLs to fetch.
    :return: list<str> The content of all the pages downloaded.
    """
    if session is None:
        raise ValueError('`session` is a required argument. You must pass an HTTP Session')
    return await asyncio.gather(
        *[
            get(url, counter, session)
            for counter, url in enumerate(urls)
        ]
    )


def get_many_using_tasks(urls: List[str], session : aiohttp.ClientSession = None) -> List[asyncio.Task]:
    if session is None:
        raise ValueError('`session` is a required argument. You must pass an HTTP Session')
    tasks = []
    for counter, url in enumerate(urls):
        mycoroutine = get(url, counter, session)
        tasks.append(asyncio.create_task(mycoroutine))
    return tasks


async def get_many_serially(urls: List[str], session: aiohttp.ClientSession = None) -> List[str]:
    if session is None:
        raise ValueError('`session` is a required argument. You must pass an HTTP Session')
    for counter, url in enumerate(urls):
        await get(url, counter, session)


def print_elapsed_time(start_time: datetime.datetime, message: str = 'Duration: '):
    """
    Prints to console a message and the duration in (minutes):(seconds) between start_time and current time.
    It removes microseconds from the time stamp.

    :param datetime.datetime start_time: should have start time obtained using datetime.datetime.utcnow()
    :param str message: Custom message to be displayed before the time duration. 
    """
    end_time = datetime.datetime.utcnow().replace(microsecond=0)
    elapsed_time = end_time - start_time.replace(microsecond=0)
    print(f'{message} {str(elapsed_time)}')



async def get_with_callback(url: str = None, counter: int = 0, session: aiohttp.ClientSession = None, _callback = None) -> str:
    """
    Get a webpage's content, given it's URL. Uses only a simple GET HTTP Request

    :param str url: A fully qualified URL to fetch.
    :param int counter: Which call is this? Order matters!
    :param aiohttp.ClientSession session: A re-usable session for making calls.
    :param callback(): function to be called when the information is received

    :return: str The result.
    """
    if session is None:
        raise ValueError('`session` is a required argument. You must pass an HTTP Session')
    logger.info(f'Awaiting {url} in call {counter}.')
    try:
        result = await session.get(url)
        logger.info(f'{url} was returned in the {counter} call.')

        if _callback:
            _callback(url, await result.text())

        return await result.text()

    except:
        logger.info(f'{url} ERROR!')
        return ''



def get_many_using_tasks_with_callback(urls: List[str], session : aiohttp.ClientSession = None, response_callback = None) -> List[asyncio.Task]:
    if session is None:
        raise ValueError('`session` is a required argument. You must pass an HTTP Session')
    tasks = []
    for counter, url in enumerate(urls):
        mycoroutine = get_with_callback(url, counter, session, response_callback)
        tasks.append(asyncio.create_task(mycoroutine))
    return tasks



def example_callback(url: str, text: str):
    """
    Simple callback example function

    :param str url: previous request url
    :param str text: response.text
    """
    print (f'example_callback: \n url:  {url}\n text size(chars): {len(text)}')



async def main():
    start_time = datetime.datetime.utcnow().replace(microsecond=0)

    urls = [URL, URL, URL, URL]
    async with aiohttp.ClientSession() as session:
        logger.info('')
        logger.info('-------------------------------------------')
        logger.info('Awaiting many pages using asyncio.Tasks')
        logger.info('-------------------------------------------')
        logger.info('-------------------------------------------')
        tasks = get_many_using_tasks_with_callback([
            'https://staging.titfortat.io',
            'https://staging.titfortat.io',
            'https://staging.titfortat.io',
            'https://staging.titfortat.io',
        ], session=session, response_callback=example_callback)
        done, pending = await asyncio.wait(tasks)


        """
        logger.info('')
        logger.info('-------------------------------------------')
        logger.info('Awaiting many pages using asyncio.gather...')
        logger.info('-------------------------------------------')
        pdb.set_trace()
        logger.info('-------------------------------------------')
        results = await get_many_using_gather(urls, session=session)
        logger.info('-------------------------------------------')
        logger.info('')
        pdb.set_trace()

        logger.info('')
        logger.info('-------------------------------------------')
        logger.info('Awaiting many pages using plain old await...')
        logger.info('-------------------------------------------')
        pdb.set_trace()
        logger.info('-------------------------------------------')
        results = await get_many_serially(urls, session=session)
        logger.info('-------------------------------------------')
        logger.info('')
        pdb.set_trace()


        logger.info('')
        logger.info('-------------------------------------------')
        logger.info('Awaiting many pages using gather on top of await...')
        results = await asyncio.gather(
            get_many_serially(urls, session=session),
            get_many_serially(urls, session=session),
            get_many_serially(urls, session=session))
        logger.info('-------------------------------------------')
        logger.info('')
        pdb.set_trace()
        """

        print_elapsed_time(start_time, "Total duration:")

if __name__ == '__main__':
    asyncio.run(main())
