import asyncio
import snakecord
import functools
import unittest
import threading

from snakecord.tests.setup import SETUP


class SnakecordTestCase(unittest.TestCase):
    @classmethod
    def _create_client(cls):
        cls.client = snakecord.Client()
        cls._have_client.set()

    @classmethod
    def setUpClass(cls):
        cls._have_client = threading.Event()
        cls.loop = asyncio.get_event_loop()

        cls.thread = threading.Thread(target=cls.loop.run_forever)
        cls.thread.start()

        cls.loop.call_soon_threadsafe(cls._create_client)
        cls._have_client.wait()

        asyncio.run_coroutine_threadsafe(cls.client.connect(SETUP['TOKEN']), cls.loop)

        async def wait():
            await cls.client.wait('cache_ready')

        future = asyncio.run_coroutine_threadsafe(wait(), cls.loop)
        future.result()

    @classmethod
    def tearDownClass(cls):
        cls.loop.stop()


def asyncTest(loop=None):
    loop = loop or asyncio.get_event_loop()

    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            future = asyncio.run_coroutine_threadsafe(func(*args, **kwargs), loop)
            return future.result()

        return wrapped

    return wrapper
