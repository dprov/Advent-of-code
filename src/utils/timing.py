import time
from functools import wraps


def timing(f):
    """Function timing decorator"""

    @wraps(f)
    def wrap(*args, **kw):
        ts = time.perf_counter()
        result = f(*args, **kw)
        te = time.perf_counter()
        # if te - ts > 0.0001:
        print(f"Function {f.__name__} took {te-ts:2.4f} seconds")
        return result

    return wrap
