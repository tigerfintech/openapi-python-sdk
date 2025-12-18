# -*- coding: utf-8 -*-
import os
from concurrent.futures import ThreadPoolExecutor


class CallbackThreadPoolExecutor:
    def __init__(self, max_workers=None):
        """
        Initializes a new OrderedThreadPoolExecutor instance.

        :param max_workers: The maximum number of threads that can be used to
            execute the given calls.
        """
        if max_workers is None or max_workers <= 0:
            max_workers = min(32, (os.cpu_count() or 1) + 4)

        self._max_workers_count = max_workers
        self._executors = [ThreadPoolExecutor(max_workers=1) for _ in range(max_workers)]

    def submit(self, fn, *args, key=None, **kwargs):
        """
        Submits a callable to be executed with the given arguments.

        Schedules the callable to be executed as fn(*args, **kwargs) and returns
        a Future instance representing the execution of the callable.

        The thread is selected based on the hash of the first argument in args.
        This ensures that calls with the same first argument are executed sequentially
        in the same thread.
        """
        if key is None:
            if args:
                key = args[0]
            else:
                key = 0
        index = abs(hash(key)) % self._max_workers_count
        return self._executors[index].submit(fn, *args, **kwargs)

    def shutdown(self, wait=True, cancel_futures=True):
        """
        Clean-up the resources associated with the Executor.

        It is safe to call this method several times. Otherwise, no other
        methods can be called after this one.

        wait: If True then shutdown will not return until all running
            futures have finished executing and the resources used by the
            executor have been reclaimed.
        cancel_futures: If True then shutdown will cancel all pending
            futures. Futures that are completed or running will not be
            cancelled.
        """
        for executor in self._executors:
            executor.shutdown(wait=wait, cancel_futures=cancel_futures)

    @property
    def _max_workers(self):
        # Expose _max_workers for compatibility with tests or inspection
        return self._max_workers_count
