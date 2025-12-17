# -*- coding: utf-8 -*-
import os
import signal
from concurrent.futures import ThreadPoolExecutor, Future


class OrderedThreadPoolExecutor:
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
        # Flag to indicate this executor has been shut down. Used to avoid
        # scheduling new tasks after shutdown is initiated (helps during
        # process termination / kill signals).
        self._shutdown = False

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
        # If executor has been shut down, return a completed Future with an
        # exception so callers don't try to schedule tasks into closed
        # threadpools (and to avoid unhandled errors printing to stderr).
        if getattr(self, '_shutdown', False):
            f = Future()
            f.set_exception(RuntimeError('executor has been shutdown'))
            return f

        index = hash(key) % self._max_workers_count
        try:
            return self._executors[index].submit(fn, *args, **kwargs)
        except RuntimeError as e:
            # Underlying ThreadPoolExecutor may have been shutdown
            # concurrently. Return a Future carrying the exception so the
            # caller receives it via the Future interface instead of an
            # unhandled thread exception.
            f = Future()
            f.set_exception(e)
            return f

    def shutdown(self, wait=True):
        """
        Clean-up the resources associated with the Executor.

        It is safe to call this method several times. Otherwise, no other
        methods can be called after this one.

        :param wait: If True then shutdown will not return until all running
            futures have finished executing and the resources used by the
            executor have been reclaimed.
        """
        # Mark shutdown first to prevent new submissions from being
        # scheduled while we're tearing down the underlying executors.
        self._shutdown = True
        for executor in self._executors:
            try:
                executor.shutdown(wait=wait)
            except Exception:
                # Ignore errors during shutdown to ensure all executors
                # are attempted to be shut down.
                pass

    @property
    def _max_workers(self):
        # Expose _max_workers for compatibility with tests or inspection
        return self._max_workers_count
