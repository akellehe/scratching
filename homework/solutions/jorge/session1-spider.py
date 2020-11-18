import logging
from typing import List
import asyncio
import sys
import aiohttp


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

async def gather_with_concurrency(n, *tasks):
    # I decided to use asyncio.semaphore to limit concurrency
    semaphore = asyncio.Semaphore(n)

    async def semaphore_task(task):
        async with semaphore:
            return await task
    return await asyncio.gather(*(semaphore_task(task) for task in tasks))

async def get(url: str = None, counter: int = 0, session: aiohttp.ClientSession = None, callback = None) -> str:
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
    await asyncio.sleep(5)
    logger.info(f'{url} was returned in the {counter} call.')
    if callback:
        callback()
    return await result.text()


def get_many_using_tasks(urls: List[str], session : aiohttp.ClientSession = None, callback = None) -> List[asyncio.Task]:
    if session is None:
        raise ValueError('`session` is a required argument. You must pass an HTTP Session')
    tasks = []
    for counter, url in enumerate(urls):
        mycoroutine = get(url, counter, session, callback)
        tasks.append(asyncio.create_task(mycoroutine))

    return tasks

def callback() -> str:
    return logger.info('CALLBACK')
async def get_many_serially(urls: List[str], session: aiohttp.ClientSession = None) -> List[str]:
    if session is None:
        raise ValueError('`session` is a required argument. You must pass an HTTP Session')
    for counter, url in enumerate(urls):
        await get(url, counter, session)


async def main():
    # Generates 100 URLs from the initial 5
    urls_sample = ['http://api.tvmaze.com/search/shows?q=girls',
            'http://api.tvmaze.com/search/shows?q=cars',
            'http://api.tvmaze.com/search/shows?q=rock',
            'http://api.tvmaze.com/search/shows?q=roll',
            'http://api.tvmaze.com/search/shows?q=adrenaline']
    urls_full_list = []
    for _ in range(0, 20):
        urls_full_list.extend(urls_sample)

    async with aiohttp.ClientSession() as session:
        logger.info('')
        logger.info('-------------------------------------------')
        logger.info('Awaiting many pages using asyncio.Tasks')
        logger.info('-------------------------------------------')
        logger.info('-------------------------------------------')
        tasks = get_many_using_tasks(urls_full_list, session=session, callback=callback)
        await gather_with_concurrency(10, *tasks)

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


if __name__ == '__main__':
    asyncio.run(main())
