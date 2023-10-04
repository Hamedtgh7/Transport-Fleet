from functools import wraps

CACHE = {}


def cached_view(func):

    @wraps(func)
    def wrapped_func(request, *args, **kwargs):
        cache_key = f'{func.__name__}-{request.get_full_path()}'

        if cache_key not in CACHE:
            CACHE[cache_key] = func(request, *args, **kwargs)
        return CACHE[cache_key]

    return wrapped_func
