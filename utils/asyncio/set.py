import asyncio


class Set:
    """
    Coroutine-safety set
    """

    def __init__(self):
        self._set = set()
        self._lock = asyncio.Lock()

    async def add(self, item):
        async with self._lock:
            self._set.add(item)

    async def remove(self, item):
        async with self._lock:
            self._set.remove(item)

    def __contains__(self, item):
        return item in self._set

    def __aiter__(self):
        return self._AsyncSetIterator(self._set)

    class _AsyncSetIterator:
        def __init__(self, async_set):
            self._async_set = async_set
            self._set_iterator = iter(self._async_set)
            self._lock = asyncio.Lock()

        async def __anext__(self):
            async with self._lock:
                try:
                    return next(self._set_iterator)
                except StopIteration as e:
                    raise StopAsyncIteration from e

    def __repr__(self):
        return f"{self.__class__.__name__}({self._set!r})"
