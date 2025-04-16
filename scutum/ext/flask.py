from scutum import Gate
from typing import Callable, Optional
from flask import Flask, Response, request
from functools import wraps

class Scutum:
    def __init__(
        self,
        app: Flask = None,
        user_resolver: Optional[Callable] = None,
        default_response: Response = Response("Unauthorized", status=403)
    ):
        self._gate = Gate()
        self._response = default_response

        self._user_resolver = self._default_resolver
        if user_resolver:
            self.set_user_resolver(user_resolver)

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.app = app
        app.extensions["scutum"] = self

    @property
    def gate(self):
        return self._gate

    def set_user_resolver(self, resolver: Callable):
        self._user_resolver = resolver

    def _default_resolver(self, *args, **kwargs):
        raise NotImplementedError("User resolver function not implemented")

    def authorized(self, action: str):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                user = self._user_resolver(request, *args, **kwargs)
                if self._gate.denied(action, user, request):
                    return self._response
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def authorized_actions(self, actions: list[str]):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                user = self._user_resolver(request, *args, **kwargs)
                if self._gate.none(actions, user, request):
                    return self._response
                return func(*args, **kwargs)
            return wrapper
        return decorator