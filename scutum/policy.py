from functools import wraps

def _get_method(obj, method):
    @wraps(method)
    def get_method(*args, **kwargs):
        return method(obj, *args, **kwargs)
    return get_method

def _get_async_method(obj, method):
    @wraps(method)
    async def get_method(*args, **kwargs):
        return await method(obj, *args, **kwargs)
    return get_method

class BasePolicy:
    _method_wrapper = staticmethod(_get_method)

    @classmethod
    def _to_actions(cls):
        obj = cls()

        actions = {}
        for name, value in cls.__dict__.items():
            if callable(value) and not name.startswith("_"):
                actions[name] = cls._method_wrapper(obj, value)
        return actions
    
class Policy(BasePolicy):
    _method_wrapper = staticmethod(_get_method)

class AsyncPolicy(BasePolicy):
    _method_wrapper = staticmethod(_get_async_method)