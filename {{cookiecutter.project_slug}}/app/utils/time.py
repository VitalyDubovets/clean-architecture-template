from time import perf_counter


class TimeCatcher:
    __slots__ = ("total_duration", "_start_time")

    def __init__(self):
        self.total_duration: float | None = None
        self._start_time: float | None = None

    async def __aenter__(self):
        self._start_time = perf_counter()
        return self

    async def __aexit__(self, *_):
        self.total_duration = perf_counter() - self._start_time
