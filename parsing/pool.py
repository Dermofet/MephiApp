import asyncio
from typing import Optional, Union

from task import PostTask, PutTask


class Pool:
    def __init__(self, max_rate: int, interval: int = 1, concurrent_level: Optional[int] = None):
        self.max_rate = max_rate
        self.interval = interval
        self.concurrent_level = concurrent_level
        self.is_running = False
        self._queue = asyncio.Queue()
        self._scheduler_task: Optional[asyncio.Task] = None
        self._sem = asyncio.Semaphore(concurrent_level or max_rate)
        self._cuncurrent_workers = 0
        self._stop_event = asyncio.Event()

    def start(self):
        self.is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler())

    async def stop(self):
        self.is_running = False
        self._scheduler_task.cancel()
        if self._cuncurrent_workers != 0:
            await self._stop_event.wait()

    async def put(self, task):
        await self._queue.put(task)

    async def join(self):
        await self._queue.join()

    async def _scheduler(self):
        while self.is_running:
            for _ in range(self.max_rate):
                async with self._sem:
                    task = await self._queue.get()
                    asyncio.create_task(self._worker(task))
            await asyncio.sleep(self.interval)

    async def _worker(self, task: Union[PostTask, PutTask]):
        async with self._sem:
            self._cuncurrent_workers += 1
            completed = await task.perform()
            self._queue.task_done()
            if not completed:
                await self.put(task)
        self._cuncurrent_workers -= 1
        if not self.is_running and self._cuncurrent_workers == 0:
            self._stop_event.set()
