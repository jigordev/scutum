from typing import Callable, Union, List
from thyros.policy import Policy
from thyros.authorizable import Authorizable
from thyros.response import Response
from thyros.exceptions import AuthorizationException, ActionNotFoundException

AuthorizationFunc = Callable[..., Union[Response, bool]]

class Singleton:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True

class Gate(Singleton):
    def __init__(self):
        self._actions = set()
        self._policies = set()
        self._map_functions = {}

    def has(self, action: str):
        return action in self._actions
    
    def actions(self):
        return self._actions
    
    def policies(self):
        return self._policies
    
    def _register_func(self, action: str, func: AuthorizationFunc):
        if callable(func):
            if action not in self._actions:
                self._actions.add(action)
                self._map_functions[action] = func
        else:
            raise TypeError("func must be a callable")

    def register(self, action: str):
        def decorator(func: AuthorizationFunc):
            self._register_func(action, func)
        return decorator
    
    def policy(self, name):
        def decorator(policy: Policy):
            if issubclass(policy, Policy):
                if name not in self._policies:
                    actions = policy._to_actions()
                    for action, func in actions.items():
                        self._register_func(f"{name}:{action}", func)
            else:
                raise TypeError("policy must be a Policy instance")
            
            return policy
        return decorator
    
    def remove(self, action: str):
        if action in self._actions:
            self._actions.remove(action)
            del self._map_functions[action]

    def check(self, action: str, user: Authorizable, *args, **kwargs) -> Union[Response, bool]:
        if action not in self._actions:
            raise ActionNotFoundException(f"Action '{action}' not found")
        
        result = self._map_functions[action](user, *args, **kwargs)
        if isinstance(result, Response):
            return result
        return bool(result)

    def allowed(self, action: str, user: Authorizable, *args, **kwargs) -> bool:
        response = self._map_functions[action](user, *args, **kwargs)
        return response.allowed if isinstance(response, Response) else response

    def denied(self, action: str, user: Authorizable, *args, **kwargs) -> bool:
        response = self._map_functions[action](user, *args, **kwargs)
        return not response.allowed if isinstance(response, Response) else response
    
    def authorize(self, action: str, user: Authorizable, *args, **kwargs) -> None:
        response = self._map_functions[action](user, *args, **kwargs)
        if isinstance(response, Response):
            response.authorize()

        if isinstance(response, bool) and not response:
            raise AuthorizationException()
    
    def any(self, actions: List[str], user: Authorizable, *args, **kwargs):
        return any([self.allowed(action, user, *args, **kwargs) for action in actions])

    def none(self, actions: List[str], user: Authorizable, *args, **kwargs):
        return not self.any(actions, user, *args, **kwargs)
