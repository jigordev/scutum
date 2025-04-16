from typing import Callable, Union, List, Any
from scutum.policy import Policy
from scutum.response import Response
from scutum.exceptions import AuthorizationException, ActionNotFoundException

AuthorizationFunc = Callable[..., Union[Response, bool]]

class Gate:
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
        
    def _register_policy(self, name: str, policy: Policy):
        if issubclass(policy, Policy):
            if name not in self._policies:
                actions = policy._to_actions()
                for action, func in actions.items():
                    self._register_func(f"{name}:{action}", func)
                self._policies.add(name)
        else:
            raise TypeError("policy must be a Policy instance")

    def register(self, action: str):
        def decorator(func: AuthorizationFunc):
            self._register_func(action, func)
            return func
        return decorator
    
    def add_action(self, action: str, func: Callable):
        self._register_func(action, func)
    
    def policy(self, name):
        def decorator(policy: Policy):
            self._register_policy(name, policy)
            return policy
        return decorator
    
    def add_policy(self, name, policy):
        self._register_policy(name, policy)
    
    def remove(self, action: str):
        if action in self._actions:
            self._actions.remove(action)
            del self._map_functions[action]

    def check(self, action: str, user: Any, *args, **kwargs) -> Union[Response, bool]:
        if action not in self._actions:
            raise ActionNotFoundException(f"Action '{action}' not found")
        
        result = self._map_functions[action](user, *args, **kwargs)
        if isinstance(result, Response):
            return result
        return bool(result)

    def allowed(self, action: str, user: Any, *args, **kwargs) -> bool:
        response = self.check(action, user, *args, **kwargs)
        if isinstance(response, Response):
            return response.allowed
        return response

    def denied(self, action: str, user: Any, *args, **kwargs) -> bool:
        response = self.check(action, user, *args, **kwargs)
        if isinstance(response, Response):
            return not response.allowed
        return not response
    
    def authorize(self, action: str, user: Any, *args, **kwargs) -> None:
        response = self.check(action, user, *args, **kwargs)
        if isinstance(response, Response):
            response.authorize()

        if isinstance(response, bool) and not response:
            raise AuthorizationException()
    
    def any(self, actions: List[str], user: Any, *args, **kwargs):
        return any([self.allowed(action, user, *args, **kwargs) for action in actions])

    def none(self, actions: List[str], user: Any, *args, **kwargs):
        return not self.any(actions, user, *args, **kwargs)
