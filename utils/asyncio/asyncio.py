import asyncio
from typing import Coroutine

def run(func: Coroutine) -> None:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        loop.create_task(func)
    else:
        asyncio.run(func)
