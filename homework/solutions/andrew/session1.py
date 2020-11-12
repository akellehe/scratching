import logging
import pdb
from typing import List
import asyncio
import sys

import aiohttp


loop = asyncio.get_event_loop()
loop.call_later()


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
    async with aiohttp.ClientSession() as session:
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
        tasks.append(asyncio.create_task(get(url, counter, session)))
    return tasks


async def get_many_serially(urls: List[str], session: aiohttp.ClientSession = None) -> List[str]:
    if session is None:
        raise ValueError('`session` is a required argument. You must pass an HTTP Session')
    for counter, url in enumerate(urls):
        await get(url, counter, session)


async def main():
    urls = [URL, URL, URL, URL]
    async with aiohttp.ClientSession() as session:
        logger.info('')
        logger.info('-------------------------------------------')
        logger.info('Awaiting many pages using asyncio.Tasks')
        logger.info('-------------------------------------------')
        pdb.set_trace()
        logger.info('-------------------------------------------')
        done, pending = await asyncio.wait(get_many_using_tasks(urls, session=session))
        logger.info('Done waiting with Tasks. That was fast!')
        logger.info('-------------------------------------------')
        logger.info('')
        pdb.set_trace()


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
        logger.info('Done.')


if __name__ == '__main__':
    asyncio.run(main())

