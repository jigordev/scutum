from typing import Any, Callable, Awaitable
from fastapi import Request, Depends, HTTPException
from scutum import AsyncGate, AuthorizationException

class FastAPIGate:
    def __init__(self, gate: AsyncGate, default_user_resolver: Callable[..., Awaitable[Any]]):
        self._gate = gate
        self._default_user_resolver = default_user_resolver

    def can(
        self,
        rule: str, 
        user_resolver: Callable[..., Awaitable[Any]] | None = None, 
        resource_resolver: Callable | None = None,
        exception: Exception | None = None
    ):
        async def dependency(
            request: Request, 
            user = Depends(user_resolver or self._default_user_resolver),
            target_id: int = None
        ):
            # Handle resource resolver properly
            if resource_resolver:
                resource = resource_resolver(request, target_id=target_id)
                args = [resource] if resource is not None else []
            else:
                args = []
            
            try:
                # Filter out request from kwargs before passing to rule
                await self._gate.authorize(rule, user, *args)
                return user
            except AuthorizationException as e:
                raise exception or HTTPException(status_code=403, detail=str(e))
        return dependency

def fastapi_adapter(gate: AsyncGate, default_user_resolver: Callable[..., Awaitable[Any]]) -> FastAPIGate:
    return FastAPIGate(gate, default_user_resolver)