import inspect
from functools import wraps
from scutum.scope import Scope, AsyncScope

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

def _get_scope(name, rules):
    scope = Scope(name)
    for rule_name, rule in rules.items():
        scope.add_rule(rule_name, rule)
    return scope

async def _get_async_scope(name, rules):
    scope = AsyncScope(name)
    for rule_name, rule in rules.items():
        await scope.add_rule(rule_name, rule)
    return scope

class BasePolicy:
    _method_wrapper = staticmethod(_get_method)
    _scope_wrapper = staticmethod(_get_scope)

    def _to_rules(self_or_cls, *args, **kwargs):
        # Check if this is being called on an instance or class
        if inspect.isclass(self_or_cls):
            # It's a class, create an instance with provided args
            cls = self_or_cls
            obj = cls(*args, **kwargs)
        else:
            # It's an instance, use it directly
            obj = self_or_cls
            cls = obj.__class__

        actions = {}
        # Get all callable attributes from the class
        for name in dir(cls):
            if not name.startswith("_"):
                method = getattr(cls, name)
                if callable(method):
                    # Check if it's defined in this class (not inherited)
                    # Extract just the class name from qualname (handles local classes)
                    qualname_parts = method.__qualname__.split('.')
                    if len(qualname_parts) >= 2 and qualname_parts[-2] == cls.__name__:
                        actions[name] = cls._method_wrapper(obj, method)
        return actions
    
    def _to_scope(self_or_cls, name):
        # Handle both classmethod and instance method calls
        if inspect.isclass(self_or_cls):
            # It's a class, create instance and get rules
            cls = self_or_cls
            obj = cls()  # Create instance without args for class registration
            rules = obj._to_rules()
            return cls._scope_wrapper(name, rules)
        else:
            # It's an instance, use it directly
            obj = self_or_cls
            cls = obj.__class__
            rules = obj._to_rules()
            return cls._scope_wrapper(name, rules)
    
    # Make it work as both classmethod and instance method
    _to_scope = classmethod(_to_scope)
    
class Policy(BasePolicy):
    _method_wrapper = staticmethod(_get_method)
    _scope_wrapper = staticmethod(_get_scope)

class AsyncPolicy(BasePolicy):
    _method_wrapper = staticmethod(_get_async_method)
    _scope_wrapper = staticmethod(_get_async_scope)
    