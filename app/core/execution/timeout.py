import signal
from contextlib import contextmanager


class QueryTimeoutError(Exception):
    pass


@contextmanager
def query_timeout(seconds: int):
    """
    Enforces a hard execution timeout.
    If exceeded, the query is aborted.
    """

    def _handle_timeout(signum, frame):
        raise QueryTimeoutError(f"Query exceeded {seconds}s timeout")

    old_handler = signal.signal(signal.SIGALRM, _handle_timeout)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
