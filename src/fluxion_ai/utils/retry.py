""" 
fluxion_ai.utils.retry
~~~~~~~~~~~~~~~~~~~~
This module provides a decorator for retrying a function call if it raises an exception.

Functions:
    - retry: Retry a function call if it raises an exception.
"""

import time
from typing import Callable

def retry(attempts: int, delay: float = 0.0):
    """
    Retry a function call if it raises an exception.

    Args:
        attempts (int): Number of retry attempts.
        delay (float): Delay in seconds between attempts.

    Returns:
        Callable: A decorator that retries the function.
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if delay > 0:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator
