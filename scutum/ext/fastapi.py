from typing import Any, Callable
from fastapi import Depends, HTTPException
from scutum import AsyncGate

def create_api_gate(user_resolver: Callable):
    gate = AsyncGate()

    def authorized_user_factory(
        rule: str,
        status: int = 403,
        message: str = "Unauthorized",
        *args,
        **kwargs
    ) -> AsyncGate:
        async def dependency(user: Any = Depends(user_resolver)):
            if await gate.denied(rule, user, *args, **kwargs):
                raise HTTPException(status_code=status, detail=message)
            return user
        return dependency

    gate.authorized_user = authorized_user_factory
    return gate
