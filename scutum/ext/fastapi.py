from typing import Any, Callable
from fastapi import Depends, HTTPException
from scutum import Gate

def create_api_gate(user_resolver: Callable, *args, **kwargs):
    gate = Gate(*args, **kwargs)

    def authorized_user_factory(
        action: str,
        status: int = 403,
        message: str = "Unauthorized",
        *resolver_args,
        **resolver_kwargs
    ):
        def dependency(user: Any = Depends(user_resolver)):
            if gate.denied(action, user, *resolver_args, **resolver_kwargs):
                raise HTTPException(status_code=status, detail=message)
            return user
        return dependency

    gate.authorized_user = authorized_user_factory
    return gate
